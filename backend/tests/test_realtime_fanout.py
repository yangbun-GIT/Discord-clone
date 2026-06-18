from typing import Any

from app.realtime import fanout
from app.realtime.events import RealtimeGatewayEvent


class FakeGatewayManager:
    def __init__(self) -> None:
        self.dm_syncs: list[tuple[int, set[int]]] = []
        self.channel_syncs: list[tuple[int, int]] = []
        self.guild_syncs: list[tuple[int, set[int], set[int]]] = []
        self.broadcasts: list[tuple[str, int, str, dict[str, Any]]] = []

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
