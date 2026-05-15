import time
from typing import Any

from app.gateway.manager import GatewayConnectionManager
from app.gateway.opcodes import Opcode


class FakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.closed: tuple[int, str] | None = None
        self.sent: list[dict[str, Any]] = []

    async def accept(self) -> None:
        self.accepted = True

    async def close(self, code: int, reason: str) -> None:
        self.closed = (code, reason)

    async def send_json(self, payload: dict[str, Any]) -> None:
        self.sent.append(payload)


async def test_reap_zombies_closes_stale_connections_only() -> None:
    manager = GatewayConnectionManager()
    stale_websocket = FakeWebSocket()
    fresh_websocket = FakeWebSocket()

    stale = await manager.connect(stale_websocket)  # type: ignore[arg-type]
    fresh = await manager.connect(fresh_websocket)  # type: ignore[arg-type]
    stale.last_heartbeat_at = time.monotonic() - 3
    fresh.last_heartbeat_at = time.monotonic()

    reaped = await manager.reap_zombies(heartbeat_interval_ms=1000)

    assert reaped == 1
    assert stale_websocket.closed == (4000, "heartbeat timeout")
    assert fresh_websocket.closed is None
    assert manager.size == 1


async def test_mark_heartbeat_prevents_zombie_reaping() -> None:
    manager = GatewayConnectionManager()
    websocket = FakeWebSocket()
    connection = await manager.connect(websocket)  # type: ignore[arg-type]
    connection.last_heartbeat_at = time.monotonic() - 3

    manager.mark_heartbeat(connection)
    reaped = await manager.reap_zombies(heartbeat_interval_ms=1000)

    assert reaped == 0
    assert websocket.closed is None
    assert manager.size == 1


async def test_broadcast_channel_removes_send_failures() -> None:
    class FailingWebSocket(FakeWebSocket):
        async def send_json(self, payload: dict[str, Any]) -> None:
            raise RuntimeError("closed")

    manager = GatewayConnectionManager()
    websocket = FailingWebSocket()
    connection = await manager.connect(websocket)  # type: ignore[arg-type]
    connection.channel_ids.add(2001)

    await manager.broadcast_channel(2001, "MESSAGE_CREATE", {"id": 1})

    assert manager.size == 0


async def test_broadcast_channel_dispatches_to_subscribers() -> None:
    manager = GatewayConnectionManager()
    websocket = FakeWebSocket()
    connection = await manager.connect(websocket)  # type: ignore[arg-type]
    connection.channel_ids.add(2001)

    await manager.broadcast_channel(2001, "MESSAGE_CREATE", {"id": 1})

    assert websocket.sent == [
        {"op": int(Opcode.DISPATCH), "d": {"id": 1}, "s": 1, "t": "MESSAGE_CREATE"}
    ]

