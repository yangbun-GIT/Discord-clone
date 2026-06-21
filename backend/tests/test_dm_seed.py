from app.repositories.dm_seed import ensure_postgres_dm_demo_workspace


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
