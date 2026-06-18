from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import ValidationError

from app.realtime.events import GATEWAY_EVENTS_CHANNEL, RealtimeGatewayEvent
from app.realtime.fanout import fanout_gateway_event
from app.realtime.redis_bus import redis_bus

MessageHandler = Callable[[RealtimeGatewayEvent], Awaitable[None]]


async def dispatch_realtime_event(event: RealtimeGatewayEvent) -> None:
    await fanout_gateway_event(event)


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
