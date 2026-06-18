from fastapi import WebSocket

from app.gateway.broadcaster import GatewayBroadcaster
from app.gateway.connection import ClientConnection, ConnectionRegistry
from app.gateway.subscriptions import SubscriptionRegistry
from app.gateway.voice_service import VoiceGatewayService
from app.gateway.zombie_reaper import GatewayReaper


class GatewayConnectionManager:
    def __init__(self) -> None:
        self._connections = ConnectionRegistry()
        self._subscriptions = SubscriptionRegistry(self._connections)
        self._broadcaster = GatewayBroadcaster(self._connections)
        self._voice = VoiceGatewayService(self._connections, self._broadcaster)
        self._reaper = GatewayReaper(self._connections)

    @property
    def size(self) -> int:
        return self._connections.size

    async def connect(self, websocket: WebSocket) -> ClientConnection:
        return await self._connections.connect(websocket)

    def disconnect(self, connection: ClientConnection) -> None:
        self._connections.disconnect(connection)

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
        await self._broadcaster.broadcast_channel(channel_id, event, data)

    async def broadcast_guild(self, guild_id: int, event: str, data: dict[str, object]) -> None:
        await self._broadcaster.broadcast_guild(guild_id, event, data)

    async def broadcast_dm(self, dm_id: int, event: str, data: dict[str, object]) -> None:
        await self._broadcaster.broadcast_dm(dm_id, event, data)

    def add_dm_to_user_subscribers(self, dm_id: int, member_ids: set[int]) -> None:
        self._subscriptions.add_dm_to_user_subscribers(dm_id, member_ids)

    async def broadcast_voice_state(
        self,
        *,
        previous_channel_id: int | None,
        channel_id: int | None,
        data: dict[str, object],
    ) -> None:
        await self._voice.broadcast_voice_state(
            previous_channel_id=previous_channel_id,
            channel_id=channel_id,
            data=data,
        )

    async def send_voice_signal(
        self,
        *,
        channel_id: int,
        target_user_id: int,
        data: dict[str, object],
    ) -> int:
        return await self._voice.send_voice_signal(
            channel_id=channel_id,
            target_user_id=target_user_id,
            data=data,
        )

    def update_voice_channel(
        self,
        connection: ClientConnection,
        channel_id: int | None,
    ) -> int | None:
        return self._subscriptions.update_voice_channel(connection, channel_id)

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
        return await self._reaper.reap_zombies(heartbeat_interval_ms=heartbeat_interval_ms)


gateway_manager = GatewayConnectionManager()
