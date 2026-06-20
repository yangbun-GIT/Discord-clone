from __future__ import annotations

from app.gateway.connection import ClientConnection, ConnectionRegistry


class SubscriptionRegistry:
    def __init__(self, connections: ConnectionRegistry) -> None:
        self._connections = connections

    def add_dm_to_user_subscribers(self, dm_id: int, member_ids: set[int]) -> None:
        for connection in self._connections.connections:
            if connection.user_id in member_ids:
                connection.dm_ids.add(dm_id)

    def add_channel_to_guild_subscribers(self, guild_id: int, channel_id: int) -> None:
        for connection in self._connections.connections:
            if guild_id in connection.guild_ids:
                connection.channel_ids.add(channel_id)

    def sync_guild_subscribers(
        self,
        guild_id: int,
        *,
        member_ids: set[int],
        channel_ids: set[int],
    ) -> None:
        for connection in self._connections.connections:
            if connection.user_id in member_ids:
                connection.guild_ids.add(guild_id)
                connection.channel_ids.update(channel_ids)
                continue
            if guild_id in connection.guild_ids:
                connection.guild_ids.discard(guild_id)
                connection.channel_ids.difference_update(channel_ids)

    def update_voice_room(
        self,
        connection: ClientConnection,
        *,
        context_type: str,
        guild_id: int | None = None,
        channel_id: int | None,
        dm_id: int | None = None,
    ) -> dict[str, int | str | None]:
        previous = {
            "context_type": connection.voice_context_type,
            "guild_id": connection.voice_guild_id,
            "channel_id": connection.voice_channel_id,
            "dm_id": connection.voice_dm_id,
            "room_id": connection.voice_dm_id
            if connection.voice_context_type == "dm"
            else connection.voice_channel_id,
        }
        if context_type == "dm" and dm_id is not None and channel_id is not None:
            connection.voice_context_type = "dm"
            connection.voice_guild_id = None
            connection.voice_channel_id = channel_id
            connection.voice_dm_id = dm_id
            return previous
        if context_type == "guild" and guild_id is not None and channel_id is not None:
            connection.voice_context_type = "guild"
            connection.voice_guild_id = guild_id
            connection.voice_channel_id = channel_id
            connection.voice_dm_id = None
            return previous
        connection.voice_context_type = None
        connection.voice_guild_id = None
        connection.voice_channel_id = None
        connection.voice_dm_id = None
        return previous

    def update_voice_channel(
        self,
        connection: ClientConnection,
        *,
        guild_id: int,
        channel_id: int | None,
    ) -> int | None:
        previous = self.update_voice_room(
            connection,
            context_type="guild",
            guild_id=guild_id,
            channel_id=channel_id,
        )
        previous_channel_id = previous.get("channel_id")
        return previous_channel_id if isinstance(previous_channel_id, int) else None
