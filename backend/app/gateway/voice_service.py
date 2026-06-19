from __future__ import annotations

from app.gateway.broadcaster import GatewayBroadcaster
from app.gateway.connection import ClientConnection, ConnectionRegistry
from app.gateway.opcodes import Opcode


class VoiceGatewayService:
    def __init__(self, connections: ConnectionRegistry, broadcaster: GatewayBroadcaster) -> None:
        self._connections = connections
        self._broadcaster = broadcaster

    async def broadcast_voice_state(
        self,
        *,
        previous_channel_id: int | None,
        channel_id: int | None,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        target_channel_ids = {
            item
            for item in (previous_channel_id, channel_id)
            if item is not None
        }
        stale: list[ClientConnection] = []
        for target_channel_id in target_channel_ids:
            stale.extend(
                await self._broadcaster.broadcast_channel(
                    target_channel_id,
                    "VOICE_STATE_UPDATE",
                    data,
                )
            )
        return stale

    async def broadcast_disconnect_leave(
        self,
        connection: ClientConnection,
    ) -> list[ClientConnection]:
        if connection.user_id is None:
            return []
        if connection.voice_channel_id is None or connection.voice_guild_id is None:
            return []
        return await self.broadcast_voice_state(
            previous_channel_id=connection.voice_channel_id,
            channel_id=None,
            data={
                "guild_id": connection.voice_guild_id,
                "channel_id": None,
                "user_id": connection.user_id,
                "username": connection.username,
                "self_mute": False,
                "self_deaf": False,
            },
        )

    async def send_voice_signal(
        self,
        *,
        channel_id: int,
        target_user_id: int,
        data: dict[str, object],
    ) -> tuple[int, list[ClientConnection]]:
        sent = 0
        stale: list[ClientConnection] = []
        for connection in self._connections.connections:
            if connection.user_id != target_user_id:
                continue
            if connection.voice_channel_id != channel_id:
                continue
            try:
                await connection.send(op=Opcode.DISPATCH, data=data, event="VOICE_SIGNAL")
                sent += 1
            except RuntimeError:
                stale.append(connection)

        return sent, stale
