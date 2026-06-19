from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from app.gateway.broadcaster import GatewayBroadcaster
from app.gateway.connection import ClientConnection, ConnectionRegistry
from app.gateway.opcodes import Opcode

type StaleDisconnectHandler = Callable[[list[ClientConnection]], Awaitable[None]]
VoiceStateKey = tuple[int, int]


class VoiceGatewayService:
    def __init__(self, connections: ConnectionRegistry, broadcaster: GatewayBroadcaster) -> None:
        self._connections = connections
        self._broadcaster = broadcaster
        self._voice_states: dict[VoiceStateKey, dict[str, object]] = {}
        self._pending_disconnect_tasks: dict[VoiceStateKey, asyncio.Task[None]] = {}

    async def broadcast_voice_state(
        self,
        *,
        previous_channel_id: int | None,
        channel_id: int | None,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        state_previous_channel_id = self._sync_voice_state(data)
        target_channel_ids = {
            item
            for item in (previous_channel_id, channel_id, state_previous_channel_id)
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

    def schedule_disconnect_leave(
        self,
        connection: ClientConnection,
        *,
        grace_seconds: float,
        disconnect_stale: StaleDisconnectHandler,
    ) -> None:
        if connection.user_id is None:
            return
        if connection.voice_channel_id is None or connection.voice_guild_id is None:
            return
        guild_id = connection.voice_guild_id
        channel_id = connection.voice_channel_id
        user_id = connection.user_id
        key = (guild_id, user_id)
        if self._has_active_voice_connection(
            guild_id=guild_id,
            channel_id=channel_id,
            user_id=user_id,
        ):
            return
        self._cancel_pending_disconnect(key)
        data = {
            "guild_id": guild_id,
            "channel_id": None,
            "user_id": user_id,
            "username": connection.username,
            "self_mute": False,
            "self_deaf": False,
        }
        previous_channel_id = channel_id

        async def delayed_leave() -> None:
            try:
                await asyncio.sleep(max(0, grace_seconds))
                if self._pending_disconnect_tasks.get(key) is not task:
                    return
                if self._has_active_voice_connection(
                    guild_id=guild_id,
                    channel_id=previous_channel_id,
                    user_id=user_id,
                ):
                    self._pending_disconnect_tasks.pop(key, None)
                    return
                self._pending_disconnect_tasks.pop(key, None)
                stale = await self.broadcast_voice_state(
                    previous_channel_id=previous_channel_id,
                    channel_id=None,
                    data=data,
                )
                await disconnect_stale(stale)
            except asyncio.CancelledError:
                return

        task = asyncio.create_task(delayed_leave())
        self._pending_disconnect_tasks[key] = task

    async def broadcast_disconnect_leave(
        self,
        connection: ClientConnection,
    ) -> list[ClientConnection]:
        if connection.user_id is None:
            return []
        if connection.voice_channel_id is None or connection.voice_guild_id is None:
            return []
        key = (connection.voice_guild_id, connection.user_id)
        self._cancel_pending_disconnect(key)
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

    async def drain_pending_disconnects(self) -> None:
        tasks = list(self._pending_disconnect_tasks.values())
        if not tasks:
            return
        await asyncio.gather(*tasks, return_exceptions=True)

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

    def _sync_voice_state(self, data: dict[str, object]) -> int | None:
        guild_id = data.get("guild_id")
        user_id = data.get("user_id")
        if not isinstance(guild_id, int) or not isinstance(user_id, int):
            return None
        key = (guild_id, user_id)
        previous_channel_id = self._current_state_channel_id(key)
        if data.get("channel_id") is None:
            self._cancel_pending_disconnect(key)
            self._voice_states.pop(key, None)
            return previous_channel_id
        self._cancel_pending_disconnect(key)
        self._voice_states[key] = dict(data)
        return previous_channel_id

    def _current_state_channel_id(self, key: VoiceStateKey) -> int | None:
        value = self._voice_states.get(key, {}).get("channel_id")
        return value if isinstance(value, int) else None

    def _cancel_pending_disconnect(self, key: VoiceStateKey) -> None:
        task = self._pending_disconnect_tasks.pop(key, None)
        if task and not task.done():
            task.cancel()

    def _has_active_voice_connection(self, *, guild_id: int, channel_id: int, user_id: int) -> bool:
        return any(
            connection.user_id == user_id
            and connection.voice_guild_id == guild_id
            and connection.voice_channel_id == channel_id
            for connection in self._connections.connections
        )
