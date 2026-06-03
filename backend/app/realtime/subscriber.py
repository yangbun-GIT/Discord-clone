from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import ValidationError

from app.gateway.manager import gateway_manager
from app.realtime.events import GATEWAY_EVENTS_CHANNEL, RealtimeGatewayEvent
from app.realtime.redis_bus import redis_bus

MessageHandler = Callable[[RealtimeGatewayEvent], Awaitable[None]]


async def dispatch_realtime_event(event: RealtimeGatewayEvent) -> None:
    _sync_local_subscriptions(event)
    if event.channel_id is not None:
        await gateway_manager.broadcast_channel(event.channel_id, event.event, event.data)
    elif event.guild_id is not None:
        await gateway_manager.broadcast_guild(event.guild_id, event.event, event.data)
    elif event.dm_id is not None:
        await gateway_manager.broadcast_dm(event.dm_id, event.event, event.data)


async def consume_gateway_events(
    handler: MessageHandler = dispatch_realtime_event,
) -> None:
    if not redis_bus.is_connected:
        return

    client = await redis_bus.get_client()
    pubsub = client.pubsub()
    await pubsub.subscribe(GATEWAY_EVENTS_CHANNEL)
    try:
        async for message in pubsub.listen():
            event = _decode_pubsub_message(message)
            if event is None:
                continue
            await handler(event)
    except asyncio.CancelledError:
        raise
    finally:
        with contextlib.suppress(Exception):
            await pubsub.unsubscribe(GATEWAY_EVENTS_CHANNEL)
        with contextlib.suppress(Exception):
            await pubsub.aclose()


def _decode_pubsub_message(message: dict[str, Any]) -> RealtimeGatewayEvent | None:
    if message.get("type") != "message":
        return None
    try:
        return RealtimeGatewayEvent.model_validate_json(str(message.get("data", "")))
    except ValidationError:
        return None


def _sync_local_subscriptions(event: RealtimeGatewayEvent) -> None:
    if event.event == "DM_CREATE" and event.dm_id is not None:
        participants = event.data.get("participants")
        if isinstance(participants, list):
            member_ids = {
                participant.get("id")
                for participant in participants
                if isinstance(participant, dict) and isinstance(participant.get("id"), int)
            }
            gateway_manager.add_dm_to_user_subscribers(event.dm_id, member_ids)
        return

    if event.event == "CHANNEL_CREATE" and event.guild_id is not None:
        channel_id = event.data.get("id")
        if isinstance(channel_id, int):
            gateway_manager.add_channel_to_guild_subscribers(event.guild_id, channel_id)
        return

    if event.event != "GUILD_UPDATE" or event.guild_id is None:
        return

    members = event.data.get("members")
    channels = event.data.get("channels")
    if not isinstance(members, list) or not isinstance(channels, list):
        return

    member_ids = {
        member.get("id")
        for member in members
        if isinstance(member, dict) and isinstance(member.get("id"), int)
    }
    channel_ids = {
        channel.get("id")
        for channel in channels
        if isinstance(channel, dict) and isinstance(channel.get("id"), int)
    }
    gateway_manager.sync_guild_subscribers(
        event.guild_id,
        member_ids=member_ids,
        channel_ids=channel_ids,
    )
