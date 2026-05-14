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
    channel_ids: set[int] = field(default_factory=set)

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
    ) -> None:
        connection.user_id = user_id
        connection.username = username
        connection.identified = True
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
