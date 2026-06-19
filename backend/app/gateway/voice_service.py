from __future__ import annotations

from app.gateway.broadcaster import GatewayBroadcaster
from app.gateway.connection import ClientConnection, ConnectionRegistry
from app.gateway.opcodes import Opcode


class VoiceGatewayService:
    def __init__(self, connections: ConnectionRegistry, broadcaster: GatewayBroadcaster) -> None:
        self._connections = connections
        self._broadcaster = broadcaster
        self._voice_states: dict[tuple[int, int], dict[str, object]] = {}

    async def broadcast_voice_state(
        self,
        *,
        previous_channel_id: int | None,
        channel_id: int | None,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        self._sync_voice_state(data)
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

    async def send_voice_state_snapshot(
        self,
        connection: ClientConnection,
        *,
        guild_ids: set[int],
        channel_id: int | None = None,
    ) -> list[ClientConnection]:
        states = self.current_voice_states(guild_ids=guild_ids, channel_id=channel_id)
        if not states:
            return []
        try:
            await connection.send(
                op=Opcode.DISPATCH,
                event="VOICE_STATE_SNAPSHOT",
                data={
                    "guild_ids": sorted(guild_ids),
                    "channel_id": channel_id,
                    "states": states,
                },
            )
        except RuntimeError:
            return [connection]
        return []

    def current_voice_states(
        self,
        *,
        guild_ids: set[int],
        channel_id: int | None = None,
    ) -> list[dict[str, object]]:
        states = [
            state
            for state in self._voice_states.values()
            if state.get("guild_id") in guild_ids
        ]
        if channel_id is not None:
            states = [state for state in states if state.get("channel_id") == channel_id]
        return [dict(state) for state in states]

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

    def _sync_voice_state(self, data: dict[str, object]) -> None:
        guild_id = data.get("guild_id")
        user_id = data.get("user_id")
        if not isinstance(guild_id, int) or not isinstance(user_id, int):
            return
        key = (guild_id, user_id)
        if data.get("channel_id") is None:
            self._voice_states.pop(key, None)
            return
        self._voice_states[key] = dict(data)
