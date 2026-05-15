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
    MessageRead,
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
            return deepcopy(guilds)

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

    def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead:
        with self._lock:
            guild = self._find_guild(guild_id)
            if actor.id != guild.owner_id:
                raise PermissionError("create invite permission required")
            code = secrets.token_urlsafe(8)
            self._invites[code] = guild_id
            return InviteRead(code=code, guild_id=guild_id, created_by=actor.id)

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


demo_store = DemoStore()
