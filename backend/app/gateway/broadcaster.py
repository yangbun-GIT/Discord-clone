from __future__ import annotations

from collections.abc import Callable

from app.gateway.connection import ClientConnection, ConnectionRegistry
from app.gateway.opcodes import Opcode


class GatewayBroadcaster:
    def __init__(self, connections: ConnectionRegistry) -> None:
        self._connections = connections

    async def broadcast_channel(
        self,
        channel_id: int,
        event: str,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        return await self._broadcast(
            lambda connection: channel_id in connection.channel_ids,
            event,
            data,
        )

    async def broadcast_guild(
        self,
        guild_id: int,
        event: str,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        return await self._broadcast(
            lambda connection: guild_id in connection.guild_ids,
            event,
            data,
        )

    async def broadcast_dm(
        self,
        dm_id: int,
        event: str,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        return await self._broadcast(
            lambda connection: dm_id in connection.dm_ids,
            event,
            data,
        )

    async def _broadcast(
        self,
        should_send: Callable[[ClientConnection], bool],
        event: str,
        data: dict[str, object],
    ) -> list[ClientConnection]:
        stale: list[ClientConnection] = []
        for connection in self._connections.connections:
            if not should_send(connection):
                continue
            try:
                await connection.send(op=Opcode.DISPATCH, data=data, event=event)
            except RuntimeError:
                stale.append(connection)

        return stale
