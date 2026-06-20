from typing import Any

from app.realtime import fanout, publisher, subscriber
from app.realtime.events import RealtimeGatewayEvent
from app.realtime.redis_bus import RedisBus


class FakeGatewayManager:
    def __init__(self) -> None:
        self.dm_syncs: list[tuple[int, set[int]]] = []
        self.channel_syncs: list[tuple[int, int]] = []
        self.guild_syncs: list[tuple[int, set[int], set[int]]] = []
        self.broadcasts: list[tuple[str, int, str, dict[str, Any]]] = []
        self.voice_snapshot_guilds: list[int] = []

    def add_dm_to_user_subscribers(self, dm_id: int, member_ids: set[int]) -> None:
        self.dm_syncs.append((dm_id, member_ids))

    def add_channel_to_guild_subscribers(self, guild_id: int, channel_id: int) -> None:
        self.channel_syncs.append((guild_id, channel_id))

    def sync_guild_subscribers(
        self,
        guild_id: int,
        *,
        member_ids: set[int],
        channel_ids: set[int],
    ) -> None:
        self.guild_syncs.append((guild_id, member_ids, channel_ids))

    async def broadcast_channel(
        self,
        channel_id: int,
        event: str,
        data: dict[str, Any],
    ) -> None:
        self.broadcasts.append(("channel", channel_id, event, data))

    async def broadcast_guild(
        self,
        guild_id: int,
        event: str,
        data: dict[str, Any],
    ) -> None:
        self.broadcasts.append(("guild", guild_id, event, data))

    async def broadcast_dm(
        self,
        dm_id: int,
        event: str,
        data: dict[str, Any],
    ) -> None:
        self.broadcasts.append(("dm", dm_id, event, data))

    async def send_guild_voice_state_snapshots(self, guild_id: int) -> None:
        self.voice_snapshot_guilds.append(guild_id)


async def test_fanout_dm_create_syncs_dm_subscribers(monkeypatch) -> None:
    manager = FakeGatewayManager()
    monkeypatch.setattr(fanout, "gateway_manager", manager)
    event = RealtimeGatewayEvent(
        dm_id=9001,
        event="DM_CREATE",
        data={"participants": [{"id": 42}, {"id": 43}, {"id": "ignored"}]},
    )

    await fanout.fanout_gateway_event(event)

    assert manager.dm_syncs == [(9001, {42, 43})]
    assert manager.broadcasts == [("dm", 9001, "DM_CREATE", event.data)]


async def test_fanout_channel_create_syncs_guild_channel_subscribers(monkeypatch) -> None:
    manager = FakeGatewayManager()
    monkeypatch.setattr(fanout, "gateway_manager", manager)
    event = RealtimeGatewayEvent(
        guild_id=1001,
        event="CHANNEL_CREATE",
        data={"id": 2001},
    )

    await fanout.fanout_gateway_event(event)

    assert manager.channel_syncs == [(1001, 2001)]
    assert manager.broadcasts == [("guild", 1001, "CHANNEL_CREATE", event.data)]


async def test_fanout_guild_update_syncs_members_and_channels(monkeypatch) -> None:
    manager = FakeGatewayManager()
    monkeypatch.setattr(fanout, "gateway_manager", manager)
    event = RealtimeGatewayEvent(
        guild_id=1001,
        event="GUILD_UPDATE",
        data={
            "members": [{"id": 42}, {"id": 43}, {"id": None}],
            "channels": [{"id": 2001}, {"id": 2002}, {"id": "ignored"}],
        },
    )

    await fanout.fanout_gateway_event(event)

    assert manager.guild_syncs == [(1001, {42, 43}, {2001, 2002})]
    assert manager.broadcasts == [("guild", 1001, "GUILD_UPDATE", event.data)]
    assert manager.voice_snapshot_guilds == [1001]


async def test_publisher_falls_back_to_local_fanout_when_redis_publish_fails(
    monkeypatch,
) -> None:
    event = RealtimeGatewayEvent(
        channel_id=2001,
        event="MESSAGE_CREATE",
        data={"id": 1, "channel_id": 2001},
    )
    fanout_events: list[RealtimeGatewayEvent] = []

    class FailingRedisBus:
        @property
        def is_connected(self) -> bool:
            return True

        async def publish_json(self, channel: str, payload: str) -> int:
            raise ConnectionError("redis unavailable")

    async def fake_fanout(fanout_event: RealtimeGatewayEvent) -> None:
        fanout_events.append(fanout_event)

    monkeypatch.setattr(publisher, "redis_bus", FailingRedisBus())
    monkeypatch.setattr(publisher, "fanout_gateway_event", fake_fanout)

    await publisher._publish_or_broadcast(event)

    assert fanout_events == [event]


async def test_publisher_falls_back_to_local_fanout_when_redis_has_no_subscribers(
    monkeypatch,
) -> None:
    event = RealtimeGatewayEvent(
        dm_id=801,
        event="DM_MESSAGE_CREATE",
        data={"id": 1, "dm_id": 801},
    )
    fanout_events: list[RealtimeGatewayEvent] = []

    class SubscriberlessRedisBus:
        @property
        def is_connected(self) -> bool:
            return True

        async def publish_json(self, channel: str, payload: str) -> int:
            return 0

    async def fake_fanout(fanout_event: RealtimeGatewayEvent) -> None:
        fanout_events.append(fanout_event)

    monkeypatch.setattr(publisher, "redis_bus", SubscriberlessRedisBus())
    monkeypatch.setattr(publisher, "fanout_gateway_event", fake_fanout)

    await publisher._publish_or_broadcast(event)

    assert fanout_events == [event]


def test_subscriber_decodes_valid_message_and_ignores_invalid_payload() -> None:
    valid_event = RealtimeGatewayEvent(
        dm_id=801,
        event="DM_MESSAGE_CREATE",
        data={"id": 1, "dm_id": 801},
    )

    decoded = subscriber._decode_pubsub_message(
        {"type": "message", "data": valid_event.model_dump_json()},
    )
    ignored_control_message = subscriber._decode_pubsub_message(
        {"type": "subscribe", "data": "ignored"},
    )
    invalid = subscriber._decode_pubsub_message({"type": "message", "data": "{bad"})

    assert decoded == valid_event
    assert ignored_control_message is None
    assert invalid is None


async def test_redis_bus_remembers_configured_url_after_connection_failure() -> None:
    bus = RedisBus()

    await bus.connect("redis://127.0.0.1:1/0")

    assert bus.is_configured is True
    assert bus.is_connected is False
    assert bus.redis_url == "redis://127.0.0.1:1/0"
