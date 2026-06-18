import pytest

from app.domain.permissions import ALL_PERMISSIONS, Permission
from app.repositories import guild_channels as channels_module
from app.repositories import guild_common
from app.repositories import guild_invites as invites_module
from app.repositories import guild_members as members_module
from app.repositories import guild_messages as messages_module
from app.repositories import guild_roles as roles_module
from app.repositories import guilds as guilds_module
from app.repositories.guilds import GuildRepository
from app.schemas.auth import UserPublic
from app.schemas.guild import (
    ChannelCreate,
    GuildCreate,
    GuildRead,
    MemberRead,
    MemberRoleUpdate,
    RoleCreate,
)


class FakeIdGenerator:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def generate(self) -> int:
        return self.values.pop(0)


class FakeGuildDatabase:
    def __init__(
        self,
        *,
        guild_owner_id: int = 42,
        membership: bool = True,
        member_exists: bool = True,
        role_exists: bool = True,
        next_position: int = 0,
        role_permissions: list[int] | None = None,
    ) -> None:
        self.guild_owner_id = guild_owner_id
        self.membership = membership
        self.member_exists = member_exists
        self.role_exists = role_exists
        self.next_position = next_position
        self.role_permissions = role_permissions or []
        self.executed: list[tuple[str, tuple[object, ...]]] = []

    async def fetchrow(self, query: str, *args: object) -> dict[str, object] | None:
        if "FROM messages m" in query and "WHERE m.id = $1" in query:
            return {
                "id": 3001,
                "channel_id": 2001,
                "author_id": 42,
                "author_name": "yangbun",
                "guild_id": 1001,
                "type": 0,
                "owner_id": self.guild_owner_id,
            }
        if "FROM invites" in query:
            return {"guild_id": 1001}
        if "COALESCE(MAX(position)" in query:
            return {"next_position": self.next_position}
        if "FROM roles" in query:
            return {"exists": 1} if self.role_exists else None
        if "FROM guild_members" in query:
            return {"exists": 1} if self.membership and self.member_exists else None
        if "FROM guilds" in query:
            return {"id": 1001, "name": "SRS Lab", "owner_id": self.guild_owner_id}
        raise AssertionError(f"unexpected fetchrow query: {query}")

    async def fetch(self, query: str, *args: object) -> list[dict[str, object]]:
        if "SELECT r.permissions" in query:
            return [{"permissions": permission} for permission in self.role_permissions]
        if "SELECT id, guild_id, name, type, position" in query:
            return [
                {
                    "id": 2001,
                    "guild_id": 1001,
                    "name": "general",
                    "type": 0,
                    "position": 0,
                }
            ]
        if "SELECT id, guild_id, name, permissions, position" in query:
            return []
        if "SELECT u.id, u.username, u.status" in query:
            return [{"id": 42, "username": "yangbun", "status": 1}]
        if "SELECT mr.user_id, r.id, r.name" in query:
            return []
        if "FROM messages m" in query:
            return []
        raise AssertionError(f"unexpected fetch query: {query}")

    async def execute(self, query: str, *args: object) -> str:
        self.executed.append((query, args))
        if "INSERT INTO invites" in query:
            return "INSERT 0 1"
        return "OK"


def owner() -> UserPublic:
    return UserPublic(id=42, username="yangbun", status=1)


def patch_guild_repository_database(
    monkeypatch: pytest.MonkeyPatch,
    fake_database: FakeGuildDatabase,
) -> None:
    for module in (
        guilds_module,
        guild_common,
        channels_module,
        invites_module,
        members_module,
        messages_module,
        roles_module,
    ):
        monkeypatch.setattr(module, "database", fake_database)


def patch_guild_repository_id_generator(
    monkeypatch: pytest.MonkeyPatch,
    values: list[int],
) -> None:
    fake_id_generator = FakeIdGenerator(values)
    for module in (
        guilds_module,
        guild_common,
        channels_module,
        messages_module,
        roles_module,
    ):
        monkeypatch.setattr(module, "id_generator", fake_id_generator)


async def fake_read_guild(guild_row: object, user_id: int) -> GuildRead:
    return GuildRead(
        id=1001,
        name="SRS Lab",
        owner_id=42,
        permissions=ALL_PERMISSIONS,
        channels=[],
        members=[MemberRead(id=user_id, username="yangbun", status=1, role="Owner")],
        messages=[],
    )


@pytest.mark.asyncio
async def test_create_guild_writes_owner_membership_and_default_channels(
    monkeypatch: pytest.MonkeyPatch,
    ) -> None:
    fake_database = FakeGuildDatabase()
    patch_guild_repository_database(monkeypatch, fake_database)
    patch_guild_repository_id_generator(monkeypatch, [9001, 9002, 9003])

    guild = await GuildRepository().create_guild(GuildCreate(name="Project Room"), owner())

    assert guild.id == 9001
    assert guild.owner_id == 42
    assert [channel.name for channel in guild.channels] == ["general", "voice-room"]
    assert "INSERT INTO users" in fake_database.executed[0][0]
    assert "INSERT INTO guilds" in fake_database.executed[1][0]
    assert "INSERT INTO guild_members" in fake_database.executed[2][0]
    assert "INSERT INTO channels" in fake_database.executed[3][0]


@pytest.mark.asyncio
async def test_get_for_user_reads_guild_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase()
    patch_guild_repository_database(monkeypatch, fake_database)

    guild = await GuildRepository().get_for_user(1001, 42)

    assert guild is not None
    assert guild.id == 1001
    assert guild.permissions == ALL_PERMISSIONS
    assert guild.channels[0].name == "general"
    assert guild.members[0].role == "Owner"


@pytest.mark.asyncio
async def test_create_channel_allows_manage_channels_permission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_database = FakeGuildDatabase(
        guild_owner_id=42,
        next_position=2,
        role_permissions=[Permission.MANAGE_CHANNELS.value],
    )
    patch_guild_repository_database(monkeypatch, fake_database)
    patch_guild_repository_id_generator(monkeypatch, [9101])

    channel = await GuildRepository().create_channel(
        1001,
        ChannelCreate(name="qa-room", type=0),
        UserPublic(id=43, username="moderator", status=1),
    )

    assert channel.id == 9101
    assert channel.position == 2
    assert "INSERT INTO channels" in fake_database.executed[0][0]


@pytest.mark.asyncio
async def test_create_channel_rejects_member_without_permission(
    monkeypatch: pytest.MonkeyPatch,
    ) -> None:
    fake_database = FakeGuildDatabase(guild_owner_id=42)
    patch_guild_repository_database(monkeypatch, fake_database)

    with pytest.raises(PermissionError):
        await GuildRepository().create_channel(
            1001,
            ChannelCreate(name="blocked-room", type=0),
            UserPublic(id=43, username="member", status=1),
        )

    assert fake_database.executed == []


@pytest.mark.asyncio
async def test_create_invite_writes_unique_code(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase()
    patch_guild_repository_database(monkeypatch, fake_database)
    monkeypatch.setattr(invites_module.secrets, "token_urlsafe", lambda size: "invite-code")

    invite = await GuildRepository().create_invite(1001, owner())

    assert invite.code == "invite-code"
    assert invite.guild_id == 1001
    assert "INSERT INTO invites" in fake_database.executed[0][0]


@pytest.mark.asyncio
async def test_join_invite_adds_user_to_guild(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase()
    patch_guild_repository_database(monkeypatch, fake_database)

    guild = await GuildRepository().join_invite(
        "invite-code",
        UserPublic(id=43, username="joiner", status=1),
    )

    assert guild.id == 1001
    assert "INSERT INTO users" in fake_database.executed[0][0]
    assert "INSERT INTO guild_members" in fake_database.executed[1][0]


@pytest.mark.asyncio
async def test_create_role_writes_next_position(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase(next_position=3)
    patch_guild_repository_database(monkeypatch, fake_database)
    patch_guild_repository_id_generator(monkeypatch, [9201])
    monkeypatch.setattr(roles_module, "read_guild", fake_read_guild)

    guild = await GuildRepository().create_role(
        1001,
        RoleCreate(name="Moderator", permissions=16),
        owner(),
    )

    assert guild.id == 1001
    assert "INSERT INTO roles" in fake_database.executed[0][0]
    assert fake_database.executed[0][1] == (9201, 1001, "Moderator", 16, 3)


@pytest.mark.asyncio
async def test_assign_member_role_writes_member_role(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase()
    patch_guild_repository_database(monkeypatch, fake_database)
    monkeypatch.setattr(roles_module, "read_guild", fake_read_guild)

    await GuildRepository().assign_member_role(
        1001,
        43,
        MemberRoleUpdate(role_id=9201),
        owner(),
    )

    assert "INSERT INTO member_roles" in fake_database.executed[0][0]
    assert fake_database.executed[0][1] == (1001, 43, 9201)


@pytest.mark.asyncio
async def test_remove_member_role_deletes_member_role(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase()
    patch_guild_repository_database(monkeypatch, fake_database)
    monkeypatch.setattr(roles_module, "read_guild", fake_read_guild)

    await GuildRepository().remove_member_role(1001, 43, 9201, owner())

    assert "DELETE FROM member_roles" in fake_database.executed[0][0]
    assert fake_database.executed[0][1] == (1001, 43, 9201)


@pytest.mark.asyncio
async def test_remove_member_deletes_non_owner_member(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase()
    patch_guild_repository_database(monkeypatch, fake_database)
    monkeypatch.setattr(members_module, "read_guild", fake_read_guild)

    await GuildRepository().remove_member(1001, 43, owner())

    assert "DELETE FROM guild_members" in fake_database.executed[0][0]
    assert fake_database.executed[0][1] == (1001, 43)


@pytest.mark.asyncio
async def test_update_message_allows_author(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_database = FakeGuildDatabase()
    patch_guild_repository_database(monkeypatch, fake_database)

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
    patch_guild_repository_database(monkeypatch, fake_database)

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
    patch_guild_repository_database(monkeypatch, fake_database)

    with pytest.raises(PermissionError):
        await GuildRepository().update_message(
            channel_id=2001,
            message_id=3001,
            actor=UserPublic(id=43, username="member", status=1),
            content="blocked",
        )

    assert fake_database.executed == []
