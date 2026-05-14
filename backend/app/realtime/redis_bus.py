from __future__ import annotations

from typing import Any

from redis.asyncio import Redis


class RedisBus:
    def __init__(self) -> None:
        self._redis: Redis | None = None

    @property
    def is_connected(self) -> bool:
        return self._redis is not None

    async def connect(self, redis_url: str | None) -> None:
        if not redis_url:
            return
        self._redis = Redis.from_url(redis_url, decode_responses=True)
        await self._redis.ping()

    async def disconnect(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None

    async def publish_json(self, channel: str, payload: str) -> int:
        if self._redis is None:
            return 0
        return int(await self._redis.publish(channel, payload))

    async def get_client(self) -> Any:
        if self._redis is None:
            raise RuntimeError("redis is not configured")
        return self._redis


redis_bus = RedisBus()

