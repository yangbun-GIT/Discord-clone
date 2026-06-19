from app.core import operation_limits
from app.core.operation_limits import OperationLimit, allow_operation, reset_operation_limits


class FakeRedisClient:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.expirations: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, seconds: int) -> None:
        self.expirations[key] = seconds


class FakeRedisBus:
    def __init__(self, client: FakeRedisClient) -> None:
        self.client = client

    @property
    def is_connected(self) -> bool:
        return True

    async def get_client(self) -> FakeRedisClient:
        return self.client


async def test_allow_operation_uses_redis_when_connected(monkeypatch) -> None:
    client = FakeRedisClient()
    monkeypatch.setattr(operation_limits, "redis_bus", FakeRedisBus(client))
    limit = OperationLimit(capacity=2, refill_per_second=1)

    assert await allow_operation("shared-key", limit) is True
    assert await allow_operation("shared-key", limit) is True
    assert await allow_operation("shared-key", limit) is False
    assert client.expirations


async def test_allow_operation_falls_back_to_local_when_redis_fails(monkeypatch) -> None:
    class FailingRedisBus:
        @property
        def is_connected(self) -> bool:
            return True

        async def get_client(self) -> object:
            raise ConnectionError("redis down")

    reset_operation_limits()
    monkeypatch.setattr(operation_limits, "redis_bus", FailingRedisBus())
    limit = OperationLimit(capacity=1, refill_per_second=1)

    assert await allow_operation("fallback-key", limit) is True
    assert await allow_operation("fallback-key", limit) is False
    reset_operation_limits()
