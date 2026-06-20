from __future__ import annotations

import asyncio
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import asyncpg

CURRENT_SCHEMA_VERSION = "0004_server_rail_layout_table"


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

    async def execute_script(self, query: str) -> None:
        if self._pool is None:
            raise RuntimeError("database pool is not configured")
        async with self._pool.acquire() as connection:
            await connection.execute(query)

    async def migrate(self) -> None:
        await self.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        applied = await self.fetchrow(
            "SELECT version FROM schema_migrations WHERE version = $1",
            CURRENT_SCHEMA_VERSION,
        )
        if applied is not None:
            return

        schema_path = Path(__file__).with_name("schema.sql")
        schema = await asyncio.to_thread(schema_path.read_text, encoding="utf-8")
        await self.execute_script(schema)
        await self.execute(
            """
            INSERT INTO schema_migrations (version)
            VALUES ($1)
            ON CONFLICT (version) DO NOTHING
            """,
            CURRENT_SCHEMA_VERSION,
        )

    async def transaction(self) -> Any:
        if self._pool is None:
            raise RuntimeError("database pool is not configured")
        connection = await self._pool.acquire()
        return connection.transaction()


database = Database()
