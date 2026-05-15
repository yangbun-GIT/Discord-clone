import asyncio
from collections.abc import Awaitable, Callable

from app.gateway.manager import gateway_manager

Sleep = Callable[[float], Awaitable[None]]


async def reap_gateway_zombies_forever(
    *,
    heartbeat_interval_ms: int,
    sleep: Sleep = asyncio.sleep,
) -> None:
    interval_seconds = max(heartbeat_interval_ms / 1000, 1)
    while True:
        await sleep(interval_seconds)
        await gateway_manager.reap_zombies(
            heartbeat_interval_ms=heartbeat_interval_ms,
        )

