from app.repositories.dm_seed import ensure_postgres_dm_demo_workspace


class FakeIdGenerator:
    def generate(self) -> int:
        return 9001


class FakeSeedDatabase:
    def __init__(self) -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []

    async def fetchrow(self, query: str, *args: object) -> dict[str, object]:
        if "FROM relationships" in query:
            return {"count": 0}
        if "FROM direct_message_members" in query:
            return {"count": 1}
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
