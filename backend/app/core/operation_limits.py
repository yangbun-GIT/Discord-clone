from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status

from app.core.rate_limit import InMemoryTokenBucket


@dataclass(frozen=True)
class OperationLimit:
    capacity: int
    refill_per_second: float


GATEWAY_IDENTIFY_LIMIT = OperationLimit(capacity=5, refill_per_second=5 / 60)
GATEWAY_HEARTBEAT_LIMIT = OperationLimit(capacity=3, refill_per_second=2 / 30)
VOICE_STATE_LIMIT = OperationLimit(capacity=12, refill_per_second=12 / 60)
VOICE_SIGNAL_LIMIT = OperationLimit(capacity=60, refill_per_second=60 / 60)
MESSAGE_CREATE_LIMIT = OperationLimit(capacity=10, refill_per_second=10 / 10)
MESSAGE_MUTATION_LIMIT = OperationLimit(capacity=20, refill_per_second=20 / 60)

operation_limiter = InMemoryTokenBucket()


def allow_operation(key: str, limit: OperationLimit) -> bool:
    return operation_limiter.allow(
        key,
        capacity=limit.capacity,
        refill_per_second=limit.refill_per_second,
    )


def require_rest_operation(key: str, limit: OperationLimit) -> None:
    if allow_operation(key, limit):
        return
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="rate limit exceeded",
        headers={"Retry-After": "1"},
    )


def reset_operation_limits() -> None:
    operation_limiter.reset()
