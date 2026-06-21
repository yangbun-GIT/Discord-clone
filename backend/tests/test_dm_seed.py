import pytest

from app.repositories.dm_seed import (
    ADMIN_DEMO_USER_ID,
    GUIDE_USER_ID,
    ensure_postgres_dm_demo_workspace,
    reset_postgres_development_workspace,
)


class FakeIdGenerator:
    def generate(self) -> int:
        return 9001


class FakeSeedDatabase:
    def __init__(self, *, dm_count: int = 1) -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.dm_count = dm_count

    async def fetchrow(self, query: str, *args: object) -> dict[str, object]:
        if "FROM relationships" in query:
            return {"count": 0}
        if "FROM direct_message_members" in query:
            return {"count": self.dm_count}
        raise AssertionError(f"unexpected fetchrow query: {query}")

    async def execute(self, query: str, *args: object) -> str:
        self.executed.append((query, args))
        return "OK"


class FakeResetDatabase(FakeSeedDatabase):
    async def fetch(self, query: str, *args: object) -> list[dict[str, object]]:
        if "SELECT dm_id FROM direct_message_members" in query:
            return [{"dm_id": 123}, {"dm_id": 456}]
        raise AssertionError(f"unexpected fetch query: {query}")


async def find_existing_dm(_: list[int]) -> int | None:
    return None


async def test_demo_workspace_does_not_seed_self_relationship() -> None:
    database = FakeSeedDatabase()

    await ensure_postgres_dm_demo_workspace(
        database=database,
        id_generator=FakeIdGenerator(),
        user_id=701,
        find_existing_dm=find_existing_dm,
    )

    relationship_inserts = [
        args
        for query, args in database.executed
        if "INSERT INTO relationships" in query
    ]
    lock_queries = [
        query
        for query, _ in database.executed
        if "pg_advisory_lock" in query or "pg_advisory_unlock" in query
    ]
    assert lock_queries == ["SELECT pg_advisory_lock($1)", "SELECT pg_advisory_unlock($1)"]
    assert relationship_inserts
    assert all(args[0] != args[1] for args in relationship_inserts)


async def test_new_user_workspace_only_seeds_guide_relationship() -> None:
    database = FakeSeedDatabase()

    await ensure_postgres_dm_demo_workspace(
        database=database,
        id_generator=FakeIdGenerator(),
        user_id=777,
        find_existing_dm=find_existing_dm,
    )

    relationship_inserts = [
        args
        for query, args in database.executed
        if "INSERT INTO relationships" in query
    ]
    assert relationship_inserts == [(777, 700, "friend")]


async def test_new_user_workspace_seeds_one_guide_dm() -> None:
    database = FakeSeedDatabase(dm_count=0)

    await ensure_postgres_dm_demo_workspace(
        database=database,
        id_generator=FakeIdGenerator(),
        user_id=777,
        find_existing_dm=find_existing_dm,
    )

    dm_member_inserts = [
        args
        for query, args in database.executed
        if "INSERT INTO direct_message_members" in query
    ]
    message_inserts = [
        args
        for query, args in database.executed
        if "INSERT INTO direct_messages" in query
    ]
    assert dm_member_inserts == [
        (80_000_000_000_777, 777, 1),
        (80_000_000_000_777, 700, 0),
    ]
    assert len(message_inserts) == 1
    assert message_inserts[0][1:3] == (80_000_000_000_777, 700)


async def test_development_workspace_reset_rejects_guide_account() -> None:
    database = FakeResetDatabase(dm_count=0)

    with pytest.raises(PermissionError):
        await reset_postgres_development_workspace(
            database=database,
            id_generator=FakeIdGenerator(),
            user_id=GUIDE_USER_ID,
            username="Guide",
            find_existing_dm=find_existing_dm,
        )


async def test_development_workspace_reset_clears_regular_test_account_state() -> None:
    database = FakeResetDatabase(dm_count=0)

    await reset_postgres_development_workspace(
        database=database,
        id_generator=FakeIdGenerator(),
        user_id=777,
        username="regular",
        find_existing_dm=find_existing_dm,
    )

    executed_queries = [query for query, _ in database.executed]
    assert "DELETE FROM invites WHERE creator_id = $1" in executed_queries
    assert "DELETE FROM member_roles WHERE user_id = $1" in executed_queries
    assert "DELETE FROM messages WHERE author_id = $1" in executed_queries
    assert not any(
        "DELETE FROM channels WHERE guild_id = $1" in query
        for query in executed_queries
    )

    relationship_inserts = [
        args
        for query, args in database.executed
        if "INSERT INTO relationships" in query
    ]
    assert relationship_inserts == [(777, GUIDE_USER_ID)]

    dm_member_inserts = [
        args
        for query, args in database.executed
        if "INSERT INTO direct_message_members" in query
    ]
    assert dm_member_inserts == [
        (80_000_000_000_777, 777, 1),
        (80_000_000_000_777, GUIDE_USER_ID, 0),
    ]


async def test_development_workspace_reset_clears_admin_dm_state() -> None:
    database = FakeResetDatabase(dm_count=0)

    await reset_postgres_development_workspace(
        database=database,
        id_generator=FakeIdGenerator(),
        user_id=ADMIN_DEMO_USER_ID,
        username="admin",
        find_existing_dm=find_existing_dm,
    )

    executed_queries = [query for query, _ in database.executed]
    assert "DELETE FROM direct_message_channels WHERE id = ANY($1::bigint[])" in executed_queries
    assert (
        "DELETE FROM relationships WHERE user_id = $1 OR related_user_id = $1"
        in executed_queries
    )
    assert "DELETE FROM user_server_rail_layouts WHERE user_id = $1" in executed_queries
    assert any("DELETE FROM guilds" in query for query in executed_queries)
    assert any("DELETE FROM guild_members" in query for query in executed_queries)
    assert "DELETE FROM invites WHERE creator_id = $1" in executed_queries
    assert "DELETE FROM member_roles WHERE user_id = $1" in executed_queries
    assert "DELETE FROM messages WHERE author_id = $1" in executed_queries

    relationship_inserts = [
        args
        for query, args in database.executed
        if "INSERT INTO relationships" in query
    ]
    assert relationship_inserts == [(ADMIN_DEMO_USER_ID, GUIDE_USER_ID)]

    dm_member_inserts = [
        args
        for query, args in database.executed
        if "INSERT INTO direct_message_members" in query
    ]
    assert dm_member_inserts == [
        (80_000_000_000_042, ADMIN_DEMO_USER_ID, 1),
        (80_000_000_000_042, GUIDE_USER_ID, 0),
    ]
