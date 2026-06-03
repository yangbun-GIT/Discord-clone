from __future__ import annotations

import secrets
from copy import deepcopy
from threading import Lock

from app.demo.data import create_initial_guilds
from app.domain.permissions import ALL_PERMISSIONS
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.auth import UserPublic
from app.schemas.dm import (
    DmCreate,
    DmMessageCreate,
    DmMessageRead,
    DmParticipantRead,
    DmRead,
    RelationshipRead,
)
from app.schemas.guild import (
    ChannelCreate,
    ChannelRead,
    GuildCreate,
    GuildRead,
    InviteRead,
    MemberRead,
    MemberRoleUpdate,
    MessageRead,
    RoleCreate,
    RoleRead,
)
from app.schemas.message import MessageDeleteRead


class DemoStore:
    """Process-local mutable store used until PostgreSQL repositories are wired."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._id_generator = SnowflakeGenerator(worker_id=1)
        self._guilds = create_initial_guilds()
        self._invites: dict[str, int] = {}
        self._dm_profiles = self._seed_dm_profiles()
        self._relationships_by_user = self._seed_relationships()
        self._dms = self._seed_dms()

    def list_guilds(self, user_id: int | None = None) -> list[GuildRead]:
        with self._lock:
            guilds = self._guilds
            if user_id is not None:
                guilds = [
                    guild
                    for guild in self._guilds
                    if any(member.id == user_id for member in guild.members)
                ]
            visible_guilds = deepcopy(guilds)
            if user_id is not None:
                for guild in visible_guilds:
                    if user_id == guild.owner_id:
                        guild.permissions = ALL_PERMISSIONS
            return visible_guilds

    def create_guild(self, payload: GuildCreate, owner: UserPublic) -> GuildRead:
        with self._lock:
            guild_id = self._id_generator.generate()
            text_channel = ChannelRead(
                id=self._id_generator.generate(),
                guild_id=guild_id,
                name="general",
                type=0,
                position=0,
            )
            voice_channel = ChannelRead(
                id=self._id_generator.generate(),
                guild_id=guild_id,
                name="voice-room",
                type=1,
                position=1,
            )
            guild = GuildRead(
                id=guild_id,
                name=payload.name,
                owner_id=owner.id,
                permissions=ALL_PERMISSIONS,
                channels=[text_channel, voice_channel],
                members=[
                    MemberRead(
                        id=owner.id,
                        username=owner.username,
                        status=owner.status,
                        role="Owner",
                    )
                ],
                messages=[],
            )
            self._guilds.append(guild)
            return deepcopy(guild)

    def get_guild_for_user(self, guild_id: int, user: UserPublic) -> GuildRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            if not any(member.id == user.id for member in guild.members):
                raise KeyError(guild_id)
            visible_guild = deepcopy(guild)
            if user.id == visible_guild.owner_id:
                visible_guild.permissions = ALL_PERMISSIONS
            return visible_guild

    def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            if actor.id != guild.owner_id:
                raise PermissionError("create invite permission required")
            code = secrets.token_urlsafe(8)
            self._invites[code] = guild_id
            return InviteRead(code=code, guild_id=guild_id, created_by=actor.id)

    def create_role(self, guild_id: int, payload: RoleCreate, actor: UserPublic) -> GuildRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            self._require_owner(guild, actor)
            position = max((role.position for role in guild.roles), default=-1) + 1
            role = RoleRead(
                id=self._id_generator.generate(),
                guild_id=guild_id,
                name=payload.name,
                permissions=payload.permissions,
                position=position,
            )
            guild.roles.append(role)
            return deepcopy(guild)

    def assign_member_role(
        self,
        guild_id: int,
        member_id: int,
        payload: MemberRoleUpdate,
        actor: UserPublic,
    ) -> GuildRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            self._require_owner(guild, actor)
            member = self._find_member(guild, member_id)
            role = self._find_role(guild, payload.role_id)
            if role.id not in member.role_ids:
                member.role_ids.append(role.id)
            member.role = self._member_role_label(guild, member)
            return deepcopy(guild)

    def remove_member_role(
        self,
        guild_id: int,
        member_id: int,
        role_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            self._require_owner(guild, actor)
            member = self._find_member(guild, member_id)
            self._find_role(guild, role_id)
            member.role_ids = [
                assigned_role_id
                for assigned_role_id in member.role_ids
                if assigned_role_id != role_id
            ]
            member.role = self._member_role_label(guild, member)
            return deepcopy(guild)

    def remove_member(self, guild_id: int, member_id: int, actor: UserPublic) -> GuildRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            self._require_owner(guild, actor)
            if member_id == guild.owner_id:
                raise ValueError("owner cannot be removed")
            if member_id == actor.id:
                raise ValueError("self-removal is not supported")
            self._find_member(guild, member_id)
            guild.members = [member for member in guild.members if member.id != member_id]
            return deepcopy(guild)

    def join_invite(self, code: str, user: UserPublic) -> GuildRead:
        with self._lock:
            guild_id = self._invites.get(code)
            if guild_id is None:
                raise KeyError(code)
            guild = self._find_guild(guild_id)
            if not any(member.id == user.id for member in guild.members):
                guild.members.append(
                    MemberRead(
                        id=user.id,
                        username=user.username,
                        status=user.status,
                        role="Member",
                    )
                )
            return deepcopy(guild)

    def create_channel(
        self,
        guild_id: int,
        payload: ChannelCreate,
        actor: UserPublic | None = None,
    ) -> ChannelRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            if actor is not None and actor.id != guild.owner_id:
                raise PermissionError("manage channels permission required")
            position = max((channel.position for channel in guild.channels), default=-1) + 1
            channel = ChannelRead(
                id=self._id_generator.generate(),
                guild_id=guild_id,
                name=payload.name,
                type=payload.type,
                position=position,
            )
            guild.channels.append(channel)
            return deepcopy(channel)

    def create_message(
        self,
        *,
        channel_id: int,
        author_id: int,
        author_name: str,
        content: str,
    ) -> MessageRead:
        with self._lock:
            guild = self._find_guild_by_channel(channel_id)
            if not any(member.id == author_id for member in guild.members):
                raise PermissionError("guild membership required")
            message = MessageRead(
                id=self._id_generator.generate(),
                channel_id=channel_id,
                author_id=author_id,
                author_name=author_name,
                content=content,
            )
            guild.messages.append(message)
            return deepcopy(message)

    def update_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
        content: str,
    ) -> MessageRead:
        with self._lock:
            guild = self._find_guild_by_channel(channel_id)
            message = self._find_message(guild, channel_id, message_id)
            self._require_message_author_or_owner(guild, message, actor)
            message.content = content
            return deepcopy(message)

    def delete_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> MessageDeleteRead:
        with self._lock:
            guild = self._find_guild_by_channel(channel_id)
            message = self._find_message(guild, channel_id, message_id)
            self._require_message_author_or_owner(guild, message, actor)
            guild.messages = [
                existing_message
                for existing_message in guild.messages
                if existing_message.id != message_id
            ]
            return MessageDeleteRead(id=message_id, channel_id=channel_id)

    def list_relationships(self, user_id: int) -> list[RelationshipRead]:
        with self._lock:
            return deepcopy(self._relationships_by_user.get(user_id, []))

    def list_dms(self, user: UserPublic) -> list[DmRead]:
        with self._lock:
            return [
                self._dm_view_for_user(dm, user.id)
                for dm in self._dms
                if any(participant.id == user.id for participant in dm.participants)
            ]

    def create_dm(self, payload: DmCreate, user: UserPublic) -> DmRead:
        with self._lock:
            recipient_ids = sorted(set(payload.recipient_ids))
            if user.id in recipient_ids:
                raise ValueError("direct messages cannot target the current user")

            self._ensure_user_profile(user)
            for recipient_id in recipient_ids:
                self._find_dm_profile(recipient_id)
            participant_ids = sorted({user.id, *recipient_ids})

            for dm in self._dms:
                if sorted(participant.id for participant in dm.participants) == participant_ids:
                    return self._dm_view_for_user(dm, user.id)

            participants = [
                self._dm_profiles[participant_id] for participant_id in participant_ids
            ]
            dm = DmRead(
                id=self._id_generator.generate(),
                recipient_ids=recipient_ids,
                participants=participants,
                display_name=self._dm_display_name(participants, user.id),
                status=self._dm_status(participants, user.id),
                activity=self._dm_activity(participants, user.id),
                unread_count=0,
                is_group=len(participants) > 2,
                member_count=len(participants),
                messages=[],
            )
            self._dms.append(dm)
            return self._dm_view_for_user(dm, user.id)

    def create_dm_message(
        self,
        *,
        dm_id: int,
        payload: DmMessageCreate,
        author: UserPublic,
    ) -> DmMessageRead:
        with self._lock:
            dm = self._find_dm(dm_id)
            if not any(participant.id == author.id for participant in dm.participants):
                raise PermissionError("direct message membership required")

            self._ensure_user_profile(author)
            message = DmMessageRead(
                id=self._id_generator.generate(),
                dm_id=dm_id,
                author_id=author.id,
                author_name=author.username,
                content=payload.content,
            )
            dm.messages.append(message)
            dm.unread_count = 0
            return deepcopy(message)

    def _find_guild(self, guild_id: int) -> GuildRead:
        for guild in self._guilds:
            if guild.id == guild_id:
                return guild
        raise KeyError(guild_id)

    def _find_guild_by_channel(self, channel_id: int) -> GuildRead:
        for guild in self._guilds:
            if any(channel.id == channel_id for channel in guild.channels):
                return guild
        raise KeyError(channel_id)

    def _find_member(self, guild: GuildRead, member_id: int) -> MemberRead:
        for member in guild.members:
            if member.id == member_id:
                return member
        raise KeyError(member_id)

    def _find_role(self, guild: GuildRead, role_id: int) -> RoleRead:
        for role in guild.roles:
            if role.id == role_id:
                return role
        raise KeyError(role_id)

    def _find_message(
        self,
        guild: GuildRead,
        channel_id: int,
        message_id: int,
    ) -> MessageRead:
        for message in guild.messages:
            if message.id == message_id and message.channel_id == channel_id:
                return message
        raise KeyError(message_id)

    def _find_dm(self, dm_id: int) -> DmRead:
        for dm in self._dms:
            if dm.id == dm_id:
                return dm
        raise KeyError(dm_id)

    def _find_dm_profile(self, user_id: int) -> DmParticipantRead:
        profile = self._dm_profiles.get(user_id)
        if profile is None:
            raise KeyError(user_id)
        return profile

    def _ensure_user_profile(self, user: UserPublic) -> None:
        if user.id in self._dm_profiles:
            return
        self._dm_profiles[user.id] = DmParticipantRead(
            id=user.id,
            username=user.username,
            handle=user.username.lower(),
            status="online" if user.status else "offline",
            activity=None,
        )

    def _dm_view_for_user(self, dm: DmRead, user_id: int) -> DmRead:
        visible = deepcopy(dm)
        visible.recipient_ids = [
            participant.id for participant in visible.participants if participant.id != user_id
        ]
        visible.display_name = self._dm_display_name(visible.participants, user_id)
        visible.status = self._dm_status(visible.participants, user_id)
        visible.activity = self._dm_activity(visible.participants, user_id)
        visible.is_group = len(visible.participants) > 2
        visible.member_count = len(visible.participants)
        return visible

    def _dm_display_name(self, participants: list[DmParticipantRead], user_id: int) -> str:
        others = [participant for participant in participants if participant.id != user_id]
        if not others:
            return "Direct Message"
        if len(others) == 1:
            return others[0].username
        return ", ".join(participant.username for participant in others[:3])

    def _dm_status(self, participants: list[DmParticipantRead], user_id: int) -> str:
        others = [participant for participant in participants if participant.id != user_id]
        for status_name in ("online", "idle", "dnd"):
            if any(participant.status == status_name for participant in others):
                return status_name
        return "offline"

    def _dm_activity(self, participants: list[DmParticipantRead], user_id: int) -> str | None:
        for participant in participants:
            if participant.id != user_id and participant.activity:
                return participant.activity
        return None

    def _require_owner(self, guild: GuildRead, actor: UserPublic) -> None:
        if actor.id != guild.owner_id:
            raise PermissionError("administrator permission required")

    def _require_message_author_or_owner(
        self,
        guild: GuildRead,
        message: MessageRead,
        actor: UserPublic,
    ) -> None:
        if actor.id == message.author_id or actor.id == guild.owner_id:
            return
        raise PermissionError("message author or manage messages permission required")

    def _member_role_label(self, guild: GuildRead, member: MemberRead) -> str:
        if member.id == guild.owner_id:
            return "Owner"
        assigned_names = [
            role.name
            for role in guild.roles
            if role.id in set(member.role_ids)
        ]
        if assigned_names:
            return ", ".join(assigned_names)
        return "Member"

    def _seed_dm_profiles(self) -> dict[int, DmParticipantRead]:
        return {
            42: DmParticipantRead(
                id=42,
                username="yangbun",
                handle="yangbun",
                status="online",
                activity=None,
            ),
            701: DmParticipantRead(
                id=701,
                username="Project Lead",
                handle="project.lead",
                status="online",
                activity="Reviewing the sprint board",
            ),
            702: DmParticipantRead(
                id=702,
                username="Frontend Pair",
                handle="frontend.pair",
                status="online",
                activity="Building components",
            ),
            703: DmParticipantRead(
                id=703,
                username="Backend Pair",
                handle="backend.pair",
                status="idle",
                activity="Reading API logs",
            ),
            704: DmParticipantRead(
                id=704,
                username="QA Reviewer",
                handle="qa.reviewer",
                status="offline",
                activity=None,
            ),
            705: DmParticipantRead(
                id=705,
                username="Design Critic",
                handle="design.critic",
                status="offline",
                activity=None,
            ),
        }

    def _seed_relationships(self) -> dict[int, list[RelationshipRead]]:
        return {
            42: [
                RelationshipRead(
                    id=701,
                    username="Project Lead",
                    handle="project.lead",
                    status="online",
                    activity="Reviewing the sprint board",
                    relationship="friend",
                ),
                RelationshipRead(
                    id=702,
                    username="Frontend Pair",
                    handle="frontend.pair",
                    status="online",
                    activity="Building components",
                    relationship="friend",
                ),
                RelationshipRead(
                    id=703,
                    username="Backend Pair",
                    handle="backend.pair",
                    status="idle",
                    activity="Reading API logs",
                    relationship="friend",
                ),
                RelationshipRead(
                    id=704,
                    username="QA Reviewer",
                    handle="qa.reviewer",
                    status="offline",
                    activity=None,
                    relationship="friend",
                ),
                RelationshipRead(
                    id=705,
                    username="Design Critic",
                    handle="design.critic",
                    status="offline",
                    activity=None,
                    relationship="pending_incoming",
                ),
            ]
        }

    def _seed_dms(self) -> list[DmRead]:
        seeds: list[DmRead] = []
        seed_specs = [
            (
                801,
                [42, 701],
                2,
                [
                    DmMessageRead(
                        id=8101,
                        dm_id=801,
                        author_id=701,
                        author_name="Project Lead",
                        content="Stage notes are ready for review.",
                    ),
                    DmMessageRead(
                        id=8102,
                        dm_id=801,
                        author_id=42,
                        author_name="yangbun",
                        content="I'll wire the next slice through the app shell.",
                    ),
                ],
            ),
            (
                802,
                [42, 702],
                0,
                [
                    DmMessageRead(
                        id=8201,
                        dm_id=802,
                        author_id=702,
                        author_name="Frontend Pair",
                        content="The private sidebar is ready for API data.",
                    )
                ],
            ),
            (
                803,
                [42, 701, 702, 703],
                1,
                [
                    DmMessageRead(
                        id=8301,
                        dm_id=803,
                        author_id=703,
                        author_name="Backend Pair",
                        content="DM persistence can move to PostgreSQL in Stage 7.10.",
                    )
                ],
            ),
        ]
        for dm_id, participant_ids, unread_count, messages in seed_specs:
            participants = [self._dm_profiles[participant_id] for participant_id in participant_ids]
            seeds.append(
                DmRead(
                    id=dm_id,
                    recipient_ids=[
                        participant_id
                        for participant_id in participant_ids
                        if participant_id != 42
                    ],
                    participants=participants,
                    display_name=self._dm_display_name(participants, 42),
                    status=self._dm_status(participants, 42),
                    activity=self._dm_activity(participants, 42),
                    unread_count=unread_count,
                    is_group=len(participants) > 2,
                    member_count=len(participants),
                    messages=messages,
                )
            )
        return seeds


demo_store = DemoStore()
