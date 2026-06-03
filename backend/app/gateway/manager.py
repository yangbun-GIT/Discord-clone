from __future__ import annotations

import time
from dataclasses import dataclass, field

from fastapi import WebSocket

from app.gateway.opcodes import Opcode


@dataclass(eq=False)
class ClientConnection:
    websocket: WebSocket
    user_id: int | None = None
    username: str | None = None
    identified: bool = False
    sequence: int = 0
    last_heartbeat_at: float = field(default_factory=time.monotonic)
    guild_ids: set[int] = field(default_factory=set)
    channel_ids: set[int] = field(default_factory=set)
    dm_ids: set[int] = field(default_factory=set)
    voice_channel_id: int | None = None

    async def send(
        self,
        *,
        op: Opcode,
        data: dict[str, object] | None = None,
        event: str | None = None,
    ) -> None:
        if event:
            self.sequence += 1
        await self.websocket.send_json(
            {"op": int(op), "d": data, "s": self.sequence if event else None, "t": event}
        )


class GatewayConnectionManager:
    def __init__(self) -> None:
        self._connections: set[ClientConnection] = set()

    @property
    def size(self) -> int:
        return len(self._connections)

    async def connect(self, websocket: WebSocket) -> ClientConnection:
        await websocket.accept()
        connection = ClientConnection(websocket=websocket)
        self._connections.add(connection)
        return connection

    def disconnect(self, connection: ClientConnection) -> None:
        self._connections.discard(connection)

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
        connection.user_id = user_id
        connection.username = username
        connection.identified = True
        connection.guild_ids = guild_ids or set()
        connection.channel_ids = channel_ids or set()
        connection.dm_ids = dm_ids or set()
        connection.last_heartbeat_at = time.monotonic()

    def mark_heartbeat(self, connection: ClientConnection) -> None:
        connection.last_heartbeat_at = time.monotonic()

    async def broadcast_channel(self, channel_id: int, event: str, data: dict[str, object]) -> None:
        stale: list[ClientConnection] = []
        for connection in self._connections:
            if channel_id not in connection.channel_ids:
                continue
            try:
                await connection.send(op=Opcode.DISPATCH, data=data, event=event)
            except RuntimeError:
                stale.append(connection)

        for connection in stale:
            self.disconnect(connection)

    async def broadcast_guild(self, guild_id: int, event: str, data: dict[str, object]) -> None:
        stale: list[ClientConnection] = []
        for connection in self._connections:
            if guild_id not in connection.guild_ids:
                continue
            try:
                await connection.send(op=Opcode.DISPATCH, data=data, event=event)
            except RuntimeError:
                stale.append(connection)

        for connection in stale:
            self.disconnect(connection)

    async def broadcast_dm(self, dm_id: int, event: str, data: dict[str, object]) -> None:
        stale: list[ClientConnection] = []
        for connection in self._connections:
            if dm_id not in connection.dm_ids:
                continue
            try:
                await connection.send(op=Opcode.DISPATCH, data=data, event=event)
            except RuntimeError:
                stale.append(connection)

        for connection in stale:
            self.disconnect(connection)

    def add_dm_to_user_subscribers(self, dm_id: int, member_ids: set[int]) -> None:
        for connection in self._connections:
            if connection.user_id in member_ids:
                connection.dm_ids.add(dm_id)

    async def broadcast_voice_state(
        self,
        *,
        previous_channel_id: int | None,
        channel_id: int | None,
        data: dict[str, object],
    ) -> None:
        target_channel_ids = {
            item
            for item in (previous_channel_id, channel_id)
            if item is not None
        }
        for target_channel_id in target_channel_ids:
            await self.broadcast_channel(target_channel_id, "VOICE_STATE_UPDATE", data)

    async def send_voice_signal(
        self,
        *,
        channel_id: int,
        target_user_id: int,
        data: dict[str, object],
    ) -> int:
        sent = 0
        stale: list[ClientConnection] = []
        for connection in self._connections:
            if connection.user_id != target_user_id:
                continue
            if connection.voice_channel_id != channel_id:
                continue
            try:
                await connection.send(op=Opcode.DISPATCH, data=data, event="VOICE_SIGNAL")
                sent += 1
            except RuntimeError:
                stale.append(connection)

        for connection in stale:
            self.disconnect(connection)
        return sent

    def update_voice_channel(
        self,
        connection: ClientConnection,
        channel_id: int | None,
    ) -> int | None:
        previous_channel_id = connection.voice_channel_id
        connection.voice_channel_id = channel_id
        return previous_channel_id

    def add_channel_to_guild_subscribers(self, guild_id: int, channel_id: int) -> None:
        for connection in self._connections:
            if guild_id in connection.guild_ids:
                connection.channel_ids.add(channel_id)

    def sync_guild_subscribers(
        self,
        guild_id: int,
        *,
        member_ids: set[int],
        channel_ids: set[int],
    ) -> None:
        for connection in self._connections:
            if connection.user_id in member_ids:
                connection.guild_ids.add(guild_id)
                connection.channel_ids.update(channel_ids)
                continue
            if guild_id in connection.guild_ids:
                connection.guild_ids.discard(guild_id)
                connection.channel_ids.difference_update(channel_ids)

    async def reap_zombies(self, *, heartbeat_interval_ms: int) -> int:
        now = time.monotonic()
        timeout_seconds = heartbeat_interval_ms / 1000 * 2
        stale = [
            connection
            for connection in self._connections
            if now - connection.last_heartbeat_at > timeout_seconds
        ]
        for connection in stale:
            await connection.websocket.close(code=4000, reason="heartbeat timeout")
            self.disconnect(connection)
        return len(stale)


gateway_manager = GatewayConnectionManager()
