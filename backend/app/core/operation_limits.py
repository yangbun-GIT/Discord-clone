from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass

from fastapi import HTTPException, status

from app.core.rate_limit import InMemoryTokenBucket
from app.realtime.redis_bus import redis_bus

logger = logging.getLogger("uvicorn.error")


@dataclass(frozen=True)
class OperationLimit:
    capacity: int
    refill_per_second: float


GATEWAY_IDENTIFY_LIMIT = OperationLimit(capacity=5, refill_per_second=5 / 60)
GATEWAY_HEARTBEAT_LIMIT = OperationLimit(capacity=3, refill_per_second=2 / 30)
VOICE_STATE_LIMIT = OperationLimit(capacity=12, refill_per_second=12 / 60)
VOICE_SIGNAL_LIMIT = OperationLimit(capacity=240, refill_per_second=120 / 60)
MESSAGE_CREATE_LIMIT = OperationLimit(capacity=10, refill_per_second=10 / 10)
MESSAGE_MUTATION_LIMIT = OperationLimit(capacity=20, refill_per_second=20 / 60)

operation_limiter = InMemoryTokenBucket()


async def allow_operation(key: str, limit: OperationLimit) -> bool:
    if redis_bus.is_connected:
        try:
            return await _allow_redis_operation(key, limit)
        except Exception as exc:
            logger.warning(
                "redis operation rate limit failed; using local fallback",
                extra={"error_type": type(exc).__name__},
            )
    return operation_limiter.allow(
        key,
        capacity=limit.capacity,
        refill_per_second=limit.refill_per_second,
    )


async def _allow_redis_operation(key: str, limit: OperationLimit) -> bool:
    redis = await redis_bus.get_client()
    window_seconds = max(1, math.ceil(limit.capacity / limit.refill_per_second))
    window_id = int(time.time() // window_seconds)
    redis_key = f"operation-limit:{key}:{window_id}"
    count = int(await redis.incr(redis_key))
    if count == 1:
        await redis.expire(redis_key, window_seconds + 1)
    return count <= limit.capacity


async def require_rest_operation(key: str, limit: OperationLimit) -> None:
    if await allow_operation(key, limit):
        return
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="rate limit exceeded",
        headers={"Retry-After": "1"},
    )


def reset_operation_limits() -> None:
    operation_limiter.reset()
