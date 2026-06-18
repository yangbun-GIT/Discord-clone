import pytest

from app.repositories import dms as dms_module
from app.repositories.dms import DmRepository
from app.schemas.auth import UserPublic
from app.schemas.dm import DmCreate, DmMessageCreate


class FakeIdGenerator:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def generate(self) -> int:
        return self.values.pop(0)


class FakeDmDatabase:
    def __init__(self) -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.users = {
            42: {"id": 42, "username": "yangbun", "status": 1},
            701: {"id": 701, "username": "Mina", "status": 1},
            704: {"id": 704, "username": "Haru", "status": 0},
        }
        self.profiles = {
            701: {
                "handle": "mina.study",
                "presence_status": "online",
                "activity": "Reading in voice",
            },
            704: {
                "handle": "haru.music",
                "presence_status": "offline",
                "activity": None,
            },
        }
        self.channels = {801: {"id": 801, "is_group": False}}
        self.members = {
            801: {
                42: {"unread_count": 2},
                701: {"unread_count": 0},
            }
        }
        self.messages = {
            801: [
                {
                    "id": 8101,
                    "dm_id": 801,
                    "author_id": 701,
                    "author_name": "Mina",
                    "content": "오늘 자료방 정리는 끝났어.",
                }
            ]
        }

    async def fetchrow(self, query: str, *args: object) -> dict[str, object] | None:
        if "SELECT COUNT(*) AS count FROM relationships" in query:
            return {"count": 1}
        if "SELECT COUNT(*) AS count FROM direct_message_members" in query:
            user_id = int(args[0])
            return {
                "count": sum(1 for members in self.members.values() if user_id in members)
            }
        if "SELECT unread_count" in query:
            dm_id, user_id = int(args[0]), int(args[1])
            return self.members.get(dm_id, {}).get(user_id)
        if "SELECT id, is_group FROM direct_message_channels" in query:
            return self.channels.get(int(args[0]))
        if "SELECT 1 AS exists" in query:
            dm_id, user_id = int(args[0]), int(args[1])
            return {"exists": 1} if user_id in self.members.get(dm_id, {}) else None
        if "SELECT id FROM direct_message_channels" in query:
            channel = self.channels.get(int(args[0]))
            return {"id": channel["id"]} if channel else None
        raise AssertionError(f"unexpected fetchrow query: {query}")

    async def fetch(self, query: str, *args: object) -> list[dict[str, object]]:
        if "FROM relationships r" in query:
            return [
                {
                    "id": 701,
                    "username": "Mina",
                    "handle": "mina.study",
                    "presence_status": "online",
                    "activity": "Reading in voice",
                    "relationship": "friend",
                }
            ]
        if "SELECT dm_id" in query and "WHERE user_id = $1" in query:
            user_id = int(args[0])
            return [
                {"dm_id": dm_id}
                for dm_id, members in self.members.items()
                if user_id in members
            ]
        if "FROM direct_message_members m" in query:
            dm_id = int(args[0])
            rows: list[dict[str, object]] = []
            for user_id in self.members.get(dm_id, {}):
                user = self.users[user_id]
                profile = self.profiles.get(user_id, {})
                rows.append(
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "handle": profile.get("handle", user["username"]),
                        "presence_status": profile.get("presence_status", str(user["status"])),
                        "activity": profile.get("activity"),
                    }
                )
            return rows
        if "FROM direct_messages m" in query:
            return self.messages.get(int(args[0]), [])
        if "WHERE u.id = ANY" in query:
            ids = set(args[0])
            rows = []
            for user_id in ids:
                user = self.users.get(user_id)
                if not user:
                    continue
                profile = self.profiles.get(user_id, {})
                rows.append(
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "handle": profile.get("handle", user["username"]),
                        "presence_status": profile.get("presence_status", str(user["status"])),
                        "activity": profile.get("activity"),
                    }
                )
            return rows
        if "SELECT dm_id, user_id FROM direct_message_members" in query:
            return [
                {"dm_id": dm_id, "user_id": user_id}
                for dm_id, members in self.members.items()
                for user_id in members
            ]
        raise AssertionError(f"unexpected fetch query: {query}")

    async def execute(self, query: str, *args: object) -> str:
        self.executed.append((query, args))
        return "OK"


def user() -> UserPublic:
    return UserPublic(id=42, username="yangbun", status=1)


@pytest.mark.asyncio
async def test_list_relationships_reads_postgres_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dms_module, "database", FakeDmDatabase())

    relationships = await DmRepository().list_relationships(42)

    assert relationships[0].id == 701
    assert relationships[0].handle == "mina.study"
    assert relationships[0].status == "online"


@pytest.mark.asyncio
async def test_create_dm_returns_existing_exact_membership(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(dms_module, "database", FakeDmDatabase())

    dm = await DmRepository().create_dm(DmCreate(recipient_ids=[701]), user())

    assert dm.id == 801
    assert dm.display_name == "Mina"
    assert dm.unread_count == 2


@pytest.mark.asyncio
async def test_create_dm_message_writes_message_and_updates_unread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_database = FakeDmDatabase()
    monkeypatch.setattr(dms_module, "database", fake_database)
    monkeypatch.setattr(dms_module, "id_generator", FakeIdGenerator([9901]))

    message = await DmRepository().create_dm_message(
        dm_id=801,
        payload=DmMessageCreate(dm_id=801, content="hello postgres dm"),
        author=user(),
    )

    assert message.id == 9901
    assert message.content == "hello postgres dm"
    assert any("INSERT INTO direct_messages" in query for query, _ in fake_database.executed)
    assert any("UPDATE direct_message_members" in query for query, _ in fake_database.executed)
