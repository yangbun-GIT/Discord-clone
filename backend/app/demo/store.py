from __future__ import annotations

from copy import deepcopy
from threading import Lock

from app.demo.data import create_initial_guilds
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.guild import ChannelCreate, ChannelRead, GuildRead, MessageRead


class DemoStore:
    """Process-local mutable store used until PostgreSQL repositories are wired."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._id_generator = SnowflakeGenerator(worker_id=1)
        self._guilds = create_initial_guilds()

    def list_guilds(self) -> list[GuildRead]:
        with self._lock:
            return deepcopy(self._guilds)

    def create_channel(self, guild_id: int, payload: ChannelCreate) -> ChannelRead:
        with self._lock:
            guild = self._find_guild(guild_id)
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

