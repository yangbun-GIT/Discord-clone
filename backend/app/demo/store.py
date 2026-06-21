from __future__ import annotations

import secrets
from copy import deepcopy
from datetime import UTC, datetime
from threading import Lock

from app.demo.data import create_initial_guilds
from app.domain.permissions import ALL_PERMISSIONS
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.auth import UserPublic
from app.schemas.dm import (
    DmCreate,
    DmDeleteRead,
    DmMessageCreate,
    DmMessageDeleteRead,
    DmMessageRead,
    DmParticipantRead,
    DmRead,
    PresenceUpdateRead,
    RelationshipDeleteRead,
    RelationshipRead,
    RelationshipState,
    UserPresenceStatus,
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
from app.schemas.user_settings import ServerRailLayout


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
        self._hidden_dm_members: set[tuple[int, int]] = set()
        self._server_rail_layouts: dict[int, ServerRailLayout] = {}

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

    def get_server_rail_layout(self, user_id: int) -> ServerRailLayout:
        with self._lock:
            layout = self._server_rail_layouts.get(user_id)
            return layout.model_copy(deep=True) if layout else ServerRailLayout()

    def set_server_rail_layout(self, user_id: int, layout: ServerRailLayout) -> ServerRailLayout:
        with self._lock:
            saved_layout = layout.model_copy(deep=True)
            self._server_rail_layouts[user_id] = saved_layout
            return saved_layout.model_copy(deep=True)

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

    def leave_guild(self, guild_id: int, actor: UserPublic) -> GuildRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            if actor.id == guild.owner_id:
                raise ValueError("owner must delete the server instead of leaving")
            self._find_member(guild, actor.id)
            guild.members = [member for member in guild.members if member.id != actor.id]
            return deepcopy(guild)

    def delete_guild(self, guild_id: int, actor: UserPublic) -> None:
        with self._lock:
            guild = self._find_guild(guild_id)
            self._require_owner(guild, actor)
            self._guilds = [
                existing_guild
                for existing_guild in self._guilds
                if existing_guild.id != guild_id
            ]
            self._invites = {
                code: invite_guild_id
                for code, invite_guild_id in self._invites.items()
                if invite_guild_id != guild_id
            }

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
                created_at=datetime.now(UTC),
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

    def update_presence(
        self,
        *,
        user: UserPublic,
        status: UserPresenceStatus,
        activity: str | None,
    ) -> tuple[PresenceUpdateRead, list[int]]:
        with self._lock:
            self._ensure_user_profile(user)
            profile = self._find_dm_profile(user.id).model_copy(
                update={
                    "status": status,
                    "activity": activity,
                },
            )
            self._dm_profiles[user.id] = profile
            self._refresh_profile_references(user.id)
            friend_user_ids = [
                relationship.id
                for relationship in self._relationships_by_user.get(user.id, [])
                if relationship.relationship == "friend"
            ]
            return (
                PresenceUpdateRead(
                    user_id=user.id,
                    username=user.username,
                    status=status,
                    activity=activity,
                ),
                friend_user_ids,
            )

    def send_friend_request(
        self,
        *,
        actor: UserPublic,
        target_username: str,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        with self._lock:
            self._ensure_user_profile(actor)
            target = self._find_dm_profile_by_username(target_username)
            if target.id == actor.id:
                raise ValueError("cannot send a friend request to yourself")
            existing = self._relationship(actor.id, target.id)
            reverse = self._relationship(target.id, actor.id)
            if existing == "blocked" or reverse == "blocked":
                raise PermissionError("relationship is blocked")
            if existing == "friend" or reverse == "friend":
                self._set_relationship(actor.id, target.id, "friend")
                self._set_relationship(target.id, actor.id, "friend")
                return self._relationship_pair(actor.id, target.id)
            if existing == "pending_incoming" and reverse == "pending_outgoing":
                return self._accept_friend_request_locked(actor.id, target.id)
            self._set_relationship(actor.id, target.id, "pending_outgoing")
            self._set_relationship(target.id, actor.id, "pending_incoming")
            return self._relationship_pair(actor.id, target.id)

    def accept_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        with self._lock:
            self._ensure_user_profile(actor)
            return self._accept_friend_request_locked(actor.id, target_user_id)

    def reject_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        with self._lock:
            self._require_relationship(actor.id, target_user_id, "pending_incoming")
            self._delete_relationship_pair(actor.id, target_user_id)
            return RelationshipDeleteRead(id=target_user_id), RelationshipDeleteRead(id=actor.id)

    def cancel_friend_request(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        with self._lock:
            self._require_relationship(actor.id, target_user_id, "pending_outgoing")
            self._delete_relationship_pair(actor.id, target_user_id)
            return RelationshipDeleteRead(id=target_user_id), RelationshipDeleteRead(id=actor.id)

    def remove_friend(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        with self._lock:
            self._require_relationship(actor.id, target_user_id, "friend")
            self._delete_relationship_pair(actor.id, target_user_id)
            return RelationshipDeleteRead(id=target_user_id), RelationshipDeleteRead(id=actor.id)

    def block_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipDeleteRead]:
        with self._lock:
            if target_user_id == actor.id:
                raise ValueError("cannot block yourself")
            self._ensure_user_profile(actor)
            self._find_dm_profile(target_user_id)
            self._set_relationship(actor.id, target_user_id, "blocked")
            self._delete_relationship(target_user_id, actor.id)
            return (
                self._relationship_read(actor.id, target_user_id),
                RelationshipDeleteRead(id=actor.id),
            )

    def unblock_user(
        self,
        *,
        actor: UserPublic,
        target_user_id: int,
    ) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
        with self._lock:
            self._require_relationship(actor.id, target_user_id, "blocked")
            self._delete_relationship(actor.id, target_user_id)
            return RelationshipDeleteRead(id=target_user_id), RelationshipDeleteRead(id=actor.id)

    def list_dms(self, user: UserPublic) -> list[DmRead]:
        with self._lock:
            return [
                self._dm_view_for_user(dm, user.id)
                for dm in self._dms
                if any(participant.id == user.id for participant in dm.participants)
                and (dm.id, user.id) not in self._hidden_dm_members
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
                    for participant_id in participant_ids:
                        self._hidden_dm_members.discard((dm.id, participant_id))
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

    def close_dm(
        self,
        *,
        dm_id: int,
        actor: UserPublic,
    ) -> DmDeleteRead:
        with self._lock:
            dm = self._find_dm(dm_id)
            if not any(participant.id == actor.id for participant in dm.participants):
                raise PermissionError("direct message membership required")
            self._hidden_dm_members.add((dm_id, actor.id))
            return DmDeleteRead(id=dm_id)

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
            if (dm_id, author.id) in self._hidden_dm_members:
                raise PermissionError("direct message membership required")

            self._ensure_user_profile(author)
            for participant in dm.participants:
                self._hidden_dm_members.discard((dm_id, participant.id))
            message = DmMessageRead(
                id=self._id_generator.generate(),
                dm_id=dm_id,
                author_id=author.id,
                author_name=author.username,
                content=payload.content,
                created_at=datetime.now(UTC),
            )
            dm.messages.append(message)
            dm.unread_count = 0
            return deepcopy(message)

    def delete_dm_message(
        self,
        *,
        dm_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> DmMessageDeleteRead:
        with self._lock:
            dm = self._find_dm(dm_id)
            if not any(participant.id == actor.id for participant in dm.participants):
                raise PermissionError("direct message membership required")
            if (dm_id, actor.id) in self._hidden_dm_members:
                raise PermissionError("direct message membership required")

            message = next((item for item in dm.messages if item.id == message_id), None)
            if message is None:
                raise KeyError(message_id)
            if message.author_id != actor.id:
                raise PermissionError("message author required")

            dm.messages = [item for item in dm.messages if item.id != message_id]
            return DmMessageDeleteRead(id=message_id, dm_id=dm_id)

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

    def _find_dm_profile_by_username(self, username: str) -> DmParticipantRead:
        normalized = username.casefold()
        for profile in self._dm_profiles.values():
            if profile.username.casefold() == normalized or profile.handle.casefold() == normalized:
                return profile
        raise KeyError(username)

    def _refresh_profile_references(self, user_id: int) -> None:
        profile = self._find_dm_profile(user_id)
        for user_relationships in self._relationships_by_user.values():
            for index, relationship in enumerate(user_relationships):
                if relationship.id == user_id:
                    user_relationships[index] = relationship.model_copy(
                        update={
                            "username": profile.username,
                            "handle": profile.handle,
                            "status": profile.status,
                            "activity": profile.activity,
                        },
                    )
        for dm in self._dms:
            dm.participants = [
                profile if participant.id == user_id else participant
                for participant in dm.participants
            ]

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

    def _relationship(self, user_id: int, related_user_id: int) -> RelationshipState | None:
        for relationship in self._relationships_by_user.get(user_id, []):
            if relationship.id == related_user_id:
                return relationship.relationship
        return None

    def _set_relationship(
        self,
        user_id: int,
        related_user_id: int,
        relationship: RelationshipState,
    ) -> None:
        next_relationship = self._relationship_read(
            user_id,
            related_user_id,
            relationship_override=relationship,
        )
        relationships = [
            item
            for item in self._relationships_by_user.get(user_id, [])
            if item.id != related_user_id
        ]
        relationships.append(next_relationship)
        relationships.sort(key=lambda item: item.username.casefold())
        self._relationships_by_user[user_id] = relationships

    def _delete_relationship(self, user_id: int, related_user_id: int) -> None:
        self._relationships_by_user[user_id] = [
            relationship
            for relationship in self._relationships_by_user.get(user_id, [])
            if relationship.id != related_user_id
        ]

    def _delete_relationship_pair(self, first_user_id: int, second_user_id: int) -> None:
        self._delete_relationship(first_user_id, second_user_id)
        self._delete_relationship(second_user_id, first_user_id)

    def _require_relationship(
        self,
        user_id: int,
        related_user_id: int,
        relationship: RelationshipState,
    ) -> None:
        if self._relationship(user_id, related_user_id) != relationship:
            raise ValueError(f"{relationship} relationship required")

    def _accept_friend_request_locked(
        self,
        actor_id: int,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        existing = self._relationship(actor_id, target_user_id)
        reverse = self._relationship(target_user_id, actor_id)
        if existing == "friend" and reverse == "friend":
            return self._relationship_pair(actor_id, target_user_id)
        if existing != "pending_incoming" or reverse != "pending_outgoing":
            raise ValueError("incoming friend request required")
        self._set_relationship(actor_id, target_user_id, "friend")
        self._set_relationship(target_user_id, actor_id, "friend")
        return self._relationship_pair(actor_id, target_user_id)

    def _relationship_pair(
        self,
        actor_id: int,
        target_user_id: int,
    ) -> tuple[RelationshipRead, RelationshipRead]:
        return (
            self._relationship_read(actor_id, target_user_id),
            self._relationship_read(target_user_id, actor_id),
        )

    def _relationship_read(
        self,
        user_id: int,
        related_user_id: int,
        *,
        relationship_override: RelationshipState | None = None,
    ) -> RelationshipRead:
        profile = self._find_dm_profile(related_user_id)
        relationship = relationship_override or self._relationship(user_id, related_user_id)
        if relationship is None:
            raise KeyError(related_user_id)
        return RelationshipRead(
            id=profile.id,
            username=profile.username,
            handle=profile.handle,
            status=profile.status,
            activity=profile.activity,
            relationship=relationship,
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
                username="admin",
                handle="admin",
                status="online",
                activity=None,
            ),
            701: DmParticipantRead(
                id=701,
                username="Mina",
                handle="mina.study",
                status="online",
                activity="Reading in voice",
            ),
            702: DmParticipantRead(
                id=702,
                username="Joon",
                handle="joon.dev",
                status="online",
                activity="Working on layout",
            ),
            703: DmParticipantRead(
                id=703,
                username="Rina",
                handle="rina.notes",
                status="idle",
                activity="Reviewing notes",
            ),
            704: DmParticipantRead(
                id=704,
                username="Haru",
                handle="haru.music",
                status="offline",
                activity=None,
            ),
            705: DmParticipantRead(
                id=705,
                username="Nora",
                handle="nora.design",
                status="offline",
                activity=None,
            ),
        }

    def _seed_relationships(self) -> dict[int, list[RelationshipRead]]:
        return {
            42: [
                RelationshipRead(
                    id=701,
                    username="Mina",
                    handle="mina.study",
                    status="online",
                    activity="Reading in voice",
                    relationship="friend",
                ),
                RelationshipRead(
                    id=702,
                    username="Joon",
                    handle="joon.dev",
                    status="online",
                    activity="Working on layout",
                    relationship="friend",
                ),
                RelationshipRead(
                    id=703,
                    username="Rina",
                    handle="rina.notes",
                    status="idle",
                    activity="Reviewing notes",
                    relationship="friend",
                ),
                RelationshipRead(
                    id=704,
                    username="Haru",
                    handle="haru.music",
                    status="offline",
                    activity=None,
                    relationship="friend",
                ),
                RelationshipRead(
                    id=705,
                    username="Nora",
                    handle="nora.design",
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
                        author_name="Mina",
                        content="오늘 자료방 정리는 끝났어.",
                    ),
                    DmMessageRead(
                        id=8102,
                        dm_id=801,
                        author_id=42,
                        author_name="admin",
                        content="좋아. 채널 목록도 더 깔끔하게 맞춰볼게.",
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
                        author_name="Joon",
                        content="저녁에 음성 채널에서 다시 얘기하자.",
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
                        author_name="Rina",
                        content="회의 전에 공유할 파일만 정리해둘게.",
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
