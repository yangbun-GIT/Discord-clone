from __future__ import annotations

import time
from dataclasses import dataclass

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


@dataclass
class Bucket:
    tokens: float
    updated_at: float


class InMemoryTokenBucket:
    def __init__(self) -> None:
        self._buckets: dict[str, Bucket] = {}

    def allow(self, key: str, *, capacity: int, refill_per_second: float) -> bool:
        now = time.monotonic()
        bucket = self._buckets.get(key)
        if bucket is None:
            self._buckets[key] = Bucket(tokens=capacity - 1, updated_at=now)
            return True

        elapsed = max(0.0, now - bucket.updated_at)
        bucket.tokens = min(capacity, bucket.tokens + elapsed * refill_per_second)
        bucket.updated_at = now

        if bucket.tokens < 1:
            return False

        bucket.tokens -= 1
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Local token bucket middleware.

    Redis-backed distributed buckets will replace this in the realtime stage.
    """

    def __init__(self, app: object) -> None:
        super().__init__(app)
        self._buckets = InMemoryTokenBucket()

    async def dispatch(self, request: Request, call_next: object) -> Response:
        if request.url.path.endswith("/health") or request.method == "OPTIONS":
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        key = f"{client_host}:{request.method}:{request.url.path}"

        if not self._buckets.allow(key, capacity=60, refill_per_second=1):
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded"},
                headers={"Retry-After": "1"},
            )

        return await call_next(request)

