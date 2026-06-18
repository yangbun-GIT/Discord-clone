from __future__ import annotations

import time

from app.gateway.connection import ConnectionRegistry


class GatewayReaper:
    def __init__(self, connections: ConnectionRegistry) -> None:
        self._connections = connections

    async def reap_zombies(self, *, heartbeat_interval_ms: int) -> int:
        now = time.monotonic()
        timeout_seconds = heartbeat_interval_ms / 1000 * 2
        stale = [
            connection
            for connection in self._connections.connections
            if now - connection.last_heartbeat_at > timeout_seconds
        ]
        for connection in stale:
            await connection.websocket.close(code=4000, reason="heartbeat timeout")
            self._connections.disconnect(connection)
        return len(stale)
