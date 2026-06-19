from __future__ import annotations

import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger("uvicorn.error")


class RedisBus:
    def __init__(self) -> None:
        self._redis: Redis | None = None
        self._redis_url: str | None = None

    @property
    def is_connected(self) -> bool:
        return self._redis is not None

    @property
    def is_configured(self) -> bool:
        return bool(self._redis_url)

    @property
    def redis_url(self) -> str | None:
        return self._redis_url

    async def connect(self, redis_url: str | None) -> None:
        self._redis_url = redis_url or self._redis_url
        if self._redis is not None:
            return
        if not redis_url:
            logger.info("redis not configured; realtime publisher uses local fallback")
            return
        redis = Redis.from_url(redis_url, decode_responses=True)
        try:
            await redis.ping()
        except RedisError as exc:
            await redis.aclose()
            self._redis = None
            logger.warning(
                "redis connection failed; realtime publisher uses local fallback",
                extra={"error_type": type(exc).__name__},
            )
            return
        self._redis = redis
        logger.warning("redis connected for realtime fanout")

    async def disconnect(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
            logger.info("redis disconnected")

    async def publish_json(self, channel: str, payload: str) -> int:
        if self._redis is None:
            return 0
        return int(await self._redis.publish(channel, payload))

    async def get_client(self) -> Any:
        if self._redis is None:
            raise RuntimeError("redis is not configured")
        return self._redis


redis_bus = RedisBus()
