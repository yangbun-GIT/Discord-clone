from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import asyncpg


class Database:
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    @property
    def is_connected(self) -> bool:
        return self._pool is not None

    async def connect(self, database_url: str | None) -> None:
        if not database_url:
            return
        self._pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=10)

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def fetch(self, query: str, *args: object) -> Sequence[asyncpg.Record]:
        if self._pool is None:
            raise RuntimeError("database pool is not configured")
        async with self._pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args: object) -> asyncpg.Record | None:
        if self._pool is None:
            raise RuntimeError("database pool is not configured")
        async with self._pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def execute(self, query: str, *args: object) -> str:
        if self._pool is None:
            raise RuntimeError("database pool is not configured")
        async with self._pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def transaction(self) -> Any:
        if self._pool is None:
            raise RuntimeError("database pool is not configured")
        connection = await self._pool.acquire()
        return connection.transaction()


database = Database()

