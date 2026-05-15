from __future__ import annotations

import secrets
from copy import deepcopy
from threading import Lock

from app.demo.data import create_initial_guilds
from app.domain.permissions import ALL_PERMISSIONS
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.auth import UserPublic
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


class DemoStore:
    """Process-local mutable store used until PostgreSQL repositories are wired."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._id_generator = SnowflakeGenerator(worker_id=1)
        self._guilds = create_initial_guilds()
        self._invites: dict[str, int] = {}

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

    def _require_owner(self, guild: GuildRead, actor: UserPublic) -> None:
        if actor.id != guild.owner_id:
            raise PermissionError("administrator permission required")

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


demo_store = DemoStore()
