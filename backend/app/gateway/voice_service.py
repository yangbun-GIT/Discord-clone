from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from app.gateway.broadcaster import GatewayBroadcaster
from app.gateway.connection import ClientConnection, ConnectionRegistry
from app.gateway.opcodes import Opcode

type StaleDisconnectHandler = Callable[[list[ClientConnection]], Awaitable[None]]
VoiceContextType = str
VoiceStateKey = tuple[VoiceContextType, int, int]
VoiceTarget = tuple[VoiceContextType, int]


class VoiceGatewayService:
    def __init__(self, connections: ConnectionRegistry, broadcaster: GatewayBroadcaster) -> None:
        self._connections = connections
        self._broadcaster = broadcaster
        self._voice_states: dict[VoiceStateKey, dict[str, object]] = {}
        self._pending_disconnect_tasks: dict[VoiceStateKey, asyncio.Task[None]] = {}

    async def broadcast_voice_state(
        self,
        *,
        previous_context_type: str | None = None,
        previous_room_id: int | None = None,
        previous_channel_id: int | None = None,
        context_type: str = "guild",
        room_id: int | None = None,
        channel_id: int | None = None,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        if room_id is None:
            room_id = channel_id
        if previous_context_type is None and previous_channel_id is not None:
            previous_context_type = "guild"
            previous_room_id = previous_channel_id
        state_previous_target = self._sync_voice_state(
            data,
            context_type=context_type,
            room_id=room_id,
        )
        target_rooms = {
            item
            for item in (
                self._make_target(previous_context_type, previous_room_id),
                self._make_target(context_type, room_id),
                state_previous_target,
            )
            if item is not None
        }
        stale: list[ClientConnection] = []
        for target_context_type, target_room_id in target_rooms:
            stale.extend(
                await self._broadcast_voice_event(target_context_type, target_room_id, data)
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
        target = self._connection_voice_target(connection)
        if target is None:
            return
        context_type, room_id = target
        guild_id = connection.voice_guild_id
        dm_id = connection.voice_dm_id
        user_id = connection.user_id
        key = (context_type, room_id, user_id)
        if self._has_active_voice_connection(
            context_type=context_type,
            room_id=room_id,
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
        if context_type == "dm":
            data["context_type"] = context_type
            data["dm_id"] = dm_id

        async def delayed_leave() -> None:
            try:
                await asyncio.sleep(max(0, grace_seconds))
                if self._pending_disconnect_tasks.get(key) is not task:
                    return
                if self._has_active_voice_connection(
                    context_type=context_type,
                    room_id=room_id,
                    user_id=user_id,
                ):
                    self._pending_disconnect_tasks.pop(key, None)
                    return
                self._pending_disconnect_tasks.pop(key, None)
                stale = await self.broadcast_voice_state(
                    previous_context_type=context_type,
                    previous_room_id=room_id,
                    context_type=context_type,
                    room_id=None,
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
        target = self._connection_voice_target(connection)
        if target is None:
            return []
        context_type, room_id = target
        key = (context_type, room_id, connection.user_id)
        self._cancel_pending_disconnect(key)
        return await self.broadcast_voice_state(
            previous_context_type=context_type,
            previous_room_id=room_id,
            context_type=context_type,
            room_id=None,
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
        dm_ids: set[int] | None = None,
        channel_id: int | None = None,
        dm_id: int | None = None,
    ) -> list[ClientConnection]:
        states = self.current_voice_states(
            guild_ids=guild_ids,
            dm_ids=dm_ids or set(),
            channel_id=channel_id,
            dm_id=dm_id,
        )
        if not states:
            return []
        payload: dict[str, object] = {
            "guild_ids": sorted(guild_ids),
            "channel_id": channel_id,
            "states": states,
        }
        if dm_ids or dm_id is not None:
            payload["dm_ids"] = sorted(dm_ids or set())
            payload["dm_id"] = dm_id
        try:
            await connection.send(
                op=Opcode.DISPATCH,
                event="VOICE_STATE_SNAPSHOT",
                data=payload,
            )
        except RuntimeError:
            return [connection]
        return []

    def current_voice_states(
        self,
        *,
        guild_ids: set[int],
        dm_ids: set[int] | None = None,
        channel_id: int | None = None,
        dm_id: int | None = None,
    ) -> list[dict[str, object]]:
        states = [
            state
            for state in self._voice_states.values()
            if (
                (
                    state.get("context_type", "guild") == "guild"
                    and state.get("guild_id") in guild_ids
                )
                or (state.get("context_type") == "dm" and state.get("dm_id") in (dm_ids or set()))
            )
        ]
        if channel_id is not None:
            states = [
                state
                for state in states
                if (
                    state.get("context_type", "guild") == "guild"
                    and state.get("channel_id") == channel_id
                )
            ]
        if dm_id is not None:
            states = [
                state
                for state in states
                if state.get("context_type") == "dm" and state.get("dm_id") == dm_id
            ]
        return [dict(state) for state in states]

    async def send_voice_signal(
        self,
        *,
        context_type: str = "guild",
        room_id: int | None = None,
        channel_id: int,
        target_user_id: int,
        data: dict[str, object],
    ) -> tuple[int, list[ClientConnection]]:
        if room_id is None:
            room_id = channel_id
        sent = 0
        stale: list[ClientConnection] = []
        for connection in self._connections.connections:
            if connection.user_id != target_user_id:
                continue
            if self._connection_voice_target(connection) != (context_type, room_id):
                continue
            try:
                await connection.send(op=Opcode.DISPATCH, data=data, event="VOICE_SIGNAL")
                sent += 1
            except RuntimeError:
                stale.append(connection)

        return sent, stale

    def _sync_voice_state(
        self,
        data: dict[str, object],
        *,
        context_type: str,
        room_id: int | None,
    ) -> VoiceTarget | None:
        user_id = data.get("user_id")
        if not isinstance(user_id, int):
            return None
        previous_key = self._current_state_key_for_user(user_id)
        previous_target = self._target_from_key(previous_key)
        if previous_key is not None:
            self._cancel_pending_disconnect(previous_key)
            self._voice_states.pop(previous_key, None)
        if room_id is None:
            return previous_target
        key = (context_type, room_id, user_id)
        self._voice_states[key] = dict(data)
        self._cancel_pending_disconnect(key)
        return previous_target

    def _current_state_key_for_user(self, user_id: int) -> VoiceStateKey | None:
        for key in self._voice_states:
            if key[2] == user_id:
                return key
        return None

    def _target_from_key(self, key: VoiceStateKey | None) -> VoiceTarget | None:
        if key is None:
            return None
        return key[0], key[1]

    def _cancel_pending_disconnect(self, key: VoiceStateKey) -> None:
        task = self._pending_disconnect_tasks.pop(key, None)
        if task and not task.done():
            task.cancel()

    def _connection_voice_target(self, connection: ClientConnection) -> VoiceTarget | None:
        if connection.voice_context_type == "dm" and connection.voice_dm_id is not None:
            return "dm", connection.voice_dm_id
        if (
            connection.voice_context_type in {None, "guild"}
            and connection.voice_channel_id is not None
        ):
            return "guild", connection.voice_channel_id
        return None

    def _make_target(self, context_type: str | None, room_id: int | None) -> VoiceTarget | None:
        if context_type in {"guild", "dm"} and room_id is not None:
            return context_type, room_id
        return None

    async def _broadcast_voice_event(
        self,
        context_type: str,
        room_id: int,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        if context_type == "dm":
            return await self._broadcaster.broadcast_dm(room_id, "VOICE_STATE_UPDATE", data)
        return await self._broadcaster.broadcast_channel(room_id, "VOICE_STATE_UPDATE", data)

    def _has_active_voice_connection(
        self,
        *,
        context_type: str,
        room_id: int,
        user_id: int,
    ) -> bool:
        return any(
            connection.user_id == user_id
            and self._connection_voice_target(connection) == (context_type, room_id)
            for connection in self._connections.connections
        )
