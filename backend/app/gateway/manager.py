from fastapi import WebSocket

from app.gateway.broadcaster import GatewayBroadcaster
from app.gateway.connection import ClientConnection, ConnectionRegistry
from app.gateway.subscriptions import SubscriptionRegistry
from app.gateway.voice_service import VoiceGatewayService
from app.gateway.zombie_reaper import GatewayReaper

VOICE_DISCONNECT_GRACE_SECONDS = 8.0


class GatewayConnectionManager:
    def __init__(
        self,
        *,
        voice_disconnect_grace_seconds: float = VOICE_DISCONNECT_GRACE_SECONDS,
    ) -> None:
        self._connections = ConnectionRegistry()
        self._subscriptions = SubscriptionRegistry(self._connections)
        self._broadcaster = GatewayBroadcaster(self._connections)
        self._voice = VoiceGatewayService(self._connections, self._broadcaster)
        self._reaper = GatewayReaper(self._connections)
        self._voice_disconnect_grace_seconds = voice_disconnect_grace_seconds

    @property
    def size(self) -> int:
        return self._connections.size

    async def connect(self, websocket: WebSocket) -> ClientConnection:
        return await self._connections.connect(websocket)

    async def disconnect(self, connection: ClientConnection, *, voice_grace: bool = True) -> None:
        if not self._connections.disconnect(connection):
            return
        if voice_grace:
            self._voice.schedule_disconnect_leave(
                connection,
                grace_seconds=self._voice_disconnect_grace_seconds,
                disconnect_stale=self._disconnect_stale,
            )
        else:
            stale = await self._voice.broadcast_disconnect_leave(connection)
            await self._disconnect_stale(stale)
        connection.voice_context_type = None
        connection.voice_guild_id = None
        connection.voice_channel_id = None
        connection.voice_dm_id = None

    def mark_identified(
        self,
        connection: ClientConnection,
        *,
        user_id: int,
        username: str | None,
        guild_ids: set[int] | None = None,
        channel_ids: set[int] | None = None,
        dm_ids: set[int] | None = None,
    ) -> None:
        self._connections.mark_identified(
            connection,
            user_id=user_id,
            username=username,
            guild_ids=guild_ids,
            channel_ids=channel_ids,
            dm_ids=dm_ids,
        )

    def mark_heartbeat(self, connection: ClientConnection) -> None:
        self._connections.mark_heartbeat(connection)

    async def broadcast_channel(self, channel_id: int, event: str, data: dict[str, object]) -> None:
        stale = await self._broadcaster.broadcast_channel(channel_id, event, data)
        await self._disconnect_stale(stale)

    async def broadcast_user(self, user_id: int, event: str, data: dict[str, object]) -> None:
        stale = await self._broadcaster.broadcast_user(user_id, event, data)
        await self._disconnect_stale(stale)

    async def broadcast_guild(self, guild_id: int, event: str, data: dict[str, object]) -> None:
        stale = await self._broadcaster.broadcast_guild(guild_id, event, data)
        await self._disconnect_stale(stale)

    async def broadcast_dm(self, dm_id: int, event: str, data: dict[str, object]) -> None:
        stale = await self._broadcaster.broadcast_dm(dm_id, event, data)
        await self._disconnect_stale(stale)

    def add_dm_to_user_subscribers(self, dm_id: int, member_ids: set[int]) -> None:
        self._subscriptions.add_dm_to_user_subscribers(dm_id, member_ids)

    async def broadcast_voice_state(
        self,
        *,
        previous_context_type: str | None = None,
        previous_room_id: int | None = None,
        previous_channel_id: int | None = None,
        context_type: str = "guild",
        room_id: int | None = None,
        channel_id: int | None,
        data: dict[str, object],
    ) -> None:
        stale = await self._voice.broadcast_voice_state(
            previous_context_type=previous_context_type,
            previous_room_id=previous_room_id,
            previous_channel_id=previous_channel_id,
            context_type=context_type,
            room_id=room_id,
            channel_id=channel_id,
            data=data,
        )
        await self._disconnect_stale(stale)

    async def send_voice_state_snapshot(
        self,
        connection: ClientConnection,
        *,
        guild_ids: set[int],
        dm_ids: set[int] | None = None,
        channel_id: int | None = None,
        dm_id: int | None = None,
    ) -> None:
        stale = await self._voice.send_voice_state_snapshot(
            connection,
            guild_ids=guild_ids,
            dm_ids=dm_ids,
            channel_id=channel_id,
            dm_id=dm_id,
        )
        await self._disconnect_stale(stale)

    async def send_voice_signal(
        self,
        *,
        context_type: str = "guild",
        room_id: int | None = None,
        channel_id: int,
        target_user_id: int,
        data: dict[str, object],
    ) -> int:
        sent, stale = await self._voice.send_voice_signal(
            context_type=context_type,
            room_id=room_id,
            channel_id=channel_id,
            target_user_id=target_user_id,
            data=data,
        )
        await self._disconnect_stale(stale)
        return sent

    def update_voice_room(
        self,
        connection: ClientConnection,
        *,
        context_type: str,
        guild_id: int | None = None,
        channel_id: int | None,
        dm_id: int | None = None,
    ) -> dict[str, int | str | None]:
        return self._subscriptions.update_voice_room(
            connection,
            context_type=context_type,
            guild_id=guild_id,
            channel_id=channel_id,
            dm_id=dm_id,
        )

    def update_voice_channel(
        self,
        connection: ClientConnection,
        *,
        guild_id: int,
        channel_id: int | None,
    ) -> int | None:
        return self._subscriptions.update_voice_channel(
            connection,
            guild_id=guild_id,
            channel_id=channel_id,
        )

    def add_channel_to_guild_subscribers(self, guild_id: int, channel_id: int) -> None:
        self._subscriptions.add_channel_to_guild_subscribers(guild_id, channel_id)

    def sync_guild_subscribers(
        self,
        guild_id: int,
        *,
        member_ids: set[int],
        channel_ids: set[int],
    ) -> None:
        self._subscriptions.sync_guild_subscribers(
            guild_id,
            member_ids=member_ids,
            channel_ids=channel_ids,
        )

    async def reap_zombies(self, *, heartbeat_interval_ms: int) -> int:
        return await self._reaper.reap_zombies(
            heartbeat_interval_ms=heartbeat_interval_ms,
            disconnect=lambda connection: self.disconnect(connection, voice_grace=False),
        )

    async def _disconnect_stale(self, connections: list[ClientConnection]) -> None:
        for connection in connections:
            await self.disconnect(connection, voice_grace=False)

    async def drain_pending_voice_disconnects(self) -> None:
        await self._voice.drain_pending_disconnects()


gateway_manager = GatewayConnectionManager()
