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


async def test_reap_zombies_broadcasts_voice_leave() -> None:
    manager = GatewayConnectionManager()
    stale_websocket = FakeWebSocket()
    observer_websocket = FakeWebSocket()
    stale = await manager.connect(stale_websocket)  # type: ignore[arg-type]
    observer = await manager.connect(observer_websocket)  # type: ignore[arg-type]
    stale.user_id = 42
    stale.username = "yangbun"
    stale.voice_guild_id = 1001
    stale.voice_channel_id = 2003
    stale.channel_ids.add(2003)
    observer.channel_ids.add(2003)
    stale.last_heartbeat_at = time.monotonic() - 3
    observer.last_heartbeat_at = time.monotonic()

    reaped = await manager.reap_zombies(heartbeat_interval_ms=1000)

    assert reaped == 1
    assert observer_websocket.sent == [
        {
            "op": int(Opcode.DISPATCH),
            "d": {
                "guild_id": 1001,
                "channel_id": None,
                "user_id": 42,
                "username": "yangbun",
                "self_mute": False,
                "self_deaf": False,
            },
            "s": 1,
            "t": "VOICE_STATE_UPDATE",
        }
    ]


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


async def test_disconnect_broadcasts_voice_leave_to_channel_subscribers() -> None:
    manager = GatewayConnectionManager()
    leaver_websocket = FakeWebSocket()
    observer_websocket = FakeWebSocket()
    leaver = await manager.connect(leaver_websocket)  # type: ignore[arg-type]
    observer = await manager.connect(observer_websocket)  # type: ignore[arg-type]
    leaver.user_id = 42
    leaver.username = "yangbun"
    leaver.voice_guild_id = 1001
    leaver.voice_channel_id = 2003
    leaver.channel_ids.add(2003)
    observer.channel_ids.add(2003)

    await manager.disconnect(leaver)

    assert manager.size == 1
    assert leaver.voice_channel_id is None
    assert observer_websocket.sent == [
        {
            "op": int(Opcode.DISPATCH),
            "d": {
                "guild_id": 1001,
                "channel_id": None,
                "user_id": 42,
                "username": "yangbun",
                "self_mute": False,
                "self_deaf": False,
            },
            "s": 1,
            "t": "VOICE_STATE_UPDATE",
        }
    ]


async def test_broadcast_channel_dispatches_to_subscribers() -> None:
    manager = GatewayConnectionManager()
    websocket = FakeWebSocket()
    connection = await manager.connect(websocket)  # type: ignore[arg-type]
    connection.channel_ids.add(2001)

    await manager.broadcast_channel(2001, "MESSAGE_CREATE", {"id": 1})

    assert websocket.sent == [
        {"op": int(Opcode.DISPATCH), "d": {"id": 1}, "s": 1, "t": "MESSAGE_CREATE"}
    ]


async def test_add_channel_to_guild_subscribers_updates_channel_subscriptions() -> None:
    manager = GatewayConnectionManager()
    websocket = FakeWebSocket()
    connection = await manager.connect(websocket)  # type: ignore[arg-type]
    connection.guild_ids.add(1001)

    manager.add_channel_to_guild_subscribers(1001, 9001)

    assert 9001 in connection.channel_ids


async def test_broadcast_dm_dispatches_to_dm_subscribers() -> None:
    manager = GatewayConnectionManager()
    target_websocket = FakeWebSocket()
    other_websocket = FakeWebSocket()
    target = await manager.connect(target_websocket)  # type: ignore[arg-type]
    other = await manager.connect(other_websocket)  # type: ignore[arg-type]
    target.dm_ids.add(801)
    other.dm_ids.add(802)

    await manager.broadcast_dm(801, "DM_MESSAGE_CREATE", {"id": 9901})

    assert target_websocket.sent == [
        {"op": int(Opcode.DISPATCH), "d": {"id": 9901}, "s": 1, "t": "DM_MESSAGE_CREATE"}
    ]
    assert other_websocket.sent == []


async def test_add_dm_to_user_subscribers_updates_dm_subscriptions() -> None:
    manager = GatewayConnectionManager()
    websocket = FakeWebSocket()
    connection = await manager.connect(websocket)  # type: ignore[arg-type]
    connection.user_id = 42

    manager.add_dm_to_user_subscribers(901, {42, 701})

    assert 901 in connection.dm_ids


async def test_sync_guild_subscribers_removes_departed_members() -> None:
    manager = GatewayConnectionManager()
    kept_websocket = FakeWebSocket()
    removed_websocket = FakeWebSocket()
    kept = await manager.connect(kept_websocket)  # type: ignore[arg-type]
    removed = await manager.connect(removed_websocket)  # type: ignore[arg-type]
    kept.user_id = 42
    removed.user_id = 43
    kept.guild_ids.add(1001)
    removed.guild_ids.add(1001)
    kept.channel_ids.update({2001, 2002})
    removed.channel_ids.update({2001, 2002})

    manager.sync_guild_subscribers(
        1001,
        member_ids={42},
        channel_ids={2001, 2002},
    )

    assert 1001 in kept.guild_ids
    assert 2001 in kept.channel_ids
    assert 1001 not in removed.guild_ids
    assert 2001 not in removed.channel_ids


async def test_send_voice_signal_targets_voice_channel_member_only() -> None:
    manager = GatewayConnectionManager()
    target_websocket = FakeWebSocket()
    other_websocket = FakeWebSocket()
    target = await manager.connect(target_websocket)  # type: ignore[arg-type]
    other = await manager.connect(other_websocket)  # type: ignore[arg-type]
    target.user_id = 43
    target.voice_channel_id = 2003
    other.user_id = 43
    other.voice_channel_id = 9001

    sent = await manager.send_voice_signal(
        channel_id=2003,
        target_user_id=43,
        data={"type": "offer"},
    )

    assert sent == 1
    assert target_websocket.sent == [
        {"op": int(Opcode.DISPATCH), "d": {"type": "offer"}, "s": 1, "t": "VOICE_SIGNAL"}
    ]
    assert other_websocket.sent == []
