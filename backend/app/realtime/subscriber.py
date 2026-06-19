from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import ValidationError

from app.realtime.events import GATEWAY_EVENTS_CHANNEL, RealtimeGatewayEvent
from app.realtime.fanout import fanout_gateway_event
from app.realtime.redis_bus import redis_bus

MessageHandler = Callable[[RealtimeGatewayEvent], Awaitable[None]]
logger = logging.getLogger("uvicorn.error")


async def dispatch_realtime_event(event: RealtimeGatewayEvent) -> None:
    await fanout_gateway_event(event)


async def consume_gateway_events(
    handler: MessageHandler = dispatch_realtime_event,
    *,
    restart_delay_seconds: float = 1.0,
) -> None:
    if not redis_bus.is_configured:
        logger.info("redis subscriber not started because redis is not connected")
        return

    while redis_bus.is_configured:
        if not redis_bus.is_connected:
            await redis_bus.connect(redis_bus.redis_url)
            if not redis_bus.is_connected:
                await asyncio.sleep(restart_delay_seconds)
                continue
        try:
            await _consume_gateway_events_once(handler)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning(
                "redis subscriber failed; restarting",
                extra={"error_type": type(exc).__name__},
            )
            await asyncio.sleep(restart_delay_seconds)


async def _consume_gateway_events_once(handler: MessageHandler) -> None:
    if not redis_bus.is_connected:
        return

    client = await redis_bus.get_client()
    pubsub = client.pubsub()
    await pubsub.subscribe(GATEWAY_EVENTS_CHANNEL)
    logger.warning("redis subscriber started", extra={"channel": GATEWAY_EVENTS_CHANNEL})
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
        logger.info("redis subscriber stopped", extra={"channel": GATEWAY_EVENTS_CHANNEL})


def _decode_pubsub_message(message: dict[str, Any]) -> RealtimeGatewayEvent | None:
    if message.get("type") != "message":
        return None
    try:
        return RealtimeGatewayEvent.model_validate_json(str(message.get("data", "")))
    except ValidationError:
        logger.warning("redis subscriber ignored invalid gateway event payload")
        return None
