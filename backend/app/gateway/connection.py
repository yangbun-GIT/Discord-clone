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
    voice_guild_id: int | None = None
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


class ConnectionRegistry:
    def __init__(self) -> None:
        self._connections: set[ClientConnection] = set()

    @property
    def connections(self) -> set[ClientConnection]:
        return self._connections

    @property
    def size(self) -> int:
        return len(self._connections)

    async def connect(self, websocket: WebSocket) -> ClientConnection:
        await websocket.accept()
        connection = ClientConnection(websocket=websocket)
        self._connections.add(connection)
        return connection

    def disconnect(self, connection: ClientConnection) -> bool:
        if connection not in self._connections:
            return False
        self._connections.discard(connection)
        return True

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
