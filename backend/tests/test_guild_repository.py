import pytest

from app.domain.permissions import Permission
from app.repositories import guilds as guilds_module
from app.repositories.guilds import GuildRepository
from app.schemas.auth import UserPublic


class FakeGuildDatabase:
    def __init__(
        self,
        *,
        membership: bool = True,
        role_permissions: list[int] | None = None,
    ) -> None:
        self.membership = membership
        self.role_permissions = role_permissions or []
        self.executed: list[tuple[str, tuple[object, ...]]] = []

    async def fetchrow(self, query: str, *args: object) -> dict[str, object] | None:
        if "FROM messages m" in query:
            return {
                "id": 3001,
                "channel_id": 2001,
                "author_id": 42,
                "author_name": "yangbun",
                "guild_id": 1001,
                "type": 0,
                "owner_id": 42,
            }
        if "FROM guild_members" in query:
            return {"exists": 1} if self.membership else None
        raise AssertionError(f"unexpected fetchrow query: {query}")

    async def fetch(self, query: str, *args: object) -> list[dict[str, object]]:
        if "SELECT r.permissions" in query:
            return [{"permissions": permission} for permission in self.role_permissions]
        raise AssertionError(f"unexpected fetch query: {query}")

    async def execute(self, query: str, *args: object) -> str:
        self.executed.append((query, args))
        return "OK"


@pytest.mark.asyncio
async def test_update_message_allows_author(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase()
    monkeypatch.setattr(guilds_module, "database", fake_database)

    message = await GuildRepository().update_message(
        channel_id=2001,
        message_id=3001,
        actor=UserPublic(id=42, username="yangbun", status=1),
        content="edited",
    )

    assert message.content == "edited"
    assert message.author_id == 42
    assert "UPDATE messages" in fake_database.executed[0][0]
    assert fake_database.executed[0][1] == ("edited", 3001, 2001)


@pytest.mark.asyncio
async def test_delete_message_allows_manage_messages_permission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_database = FakeGuildDatabase(role_permissions=[Permission.MANAGE_MESSAGES.value])
    monkeypatch.setattr(guilds_module, "database", fake_database)

    deleted = await GuildRepository().delete_message(
        channel_id=2001,
        message_id=3001,
        actor=UserPublic(id=43, username="moderator", status=1),
    )

    assert deleted.id == 3001
    assert deleted.channel_id == 2001
    assert "DELETE FROM messages" in fake_database.executed[0][0]
    assert fake_database.executed[0][1] == (3001, 2001)


@pytest.mark.asyncio
async def test_update_message_rejects_non_author_without_permission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_database = FakeGuildDatabase()
    monkeypatch.setattr(guilds_module, "database", fake_database)

    with pytest.raises(PermissionError):
        await GuildRepository().update_message(
            channel_id=2001,
            message_id=3001,
            actor=UserPublic(id=43, username="member", status=1),
            content="blocked",
        )

    assert fake_database.executed == []
