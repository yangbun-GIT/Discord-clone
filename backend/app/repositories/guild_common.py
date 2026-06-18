from __future__ import annotations

from typing import Any

from app.db.pool import database
from app.domain.permissions import ALL_PERMISSIONS, Permission, has_permission, merge_permissions
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.auth import UserPublic
from app.schemas.guild import ChannelRead, GuildRead, MemberRead, MessageRead, RoleRead

id_generator = SnowflakeGenerator(worker_id=2)
BASE_MEMBER_PERMISSIONS = merge_permissions(
    [
        Permission.READ_MESSAGES,
        Permission.SEND_MESSAGES,
        Permission.CONNECT,
        Permission.SPEAK,
    ]
)


async def ensure_user(user: UserPublic) -> None:
    await database.execute(
        """
        INSERT INTO users (id, username, password_hash, status)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (id) DO UPDATE
        SET username = EXCLUDED.username,
            status = EXCLUDED.status
        """,
        user.id,
        user.username,
        "dev-session",
        user.status,
    )


async def list_channels(guild_id: int) -> list[ChannelRead]:
    rows = await database.fetch(
        """
        SELECT id, guild_id, name, type, position
        FROM channels
        WHERE guild_id = $1
        ORDER BY position ASC, id ASC
        """,
        guild_id,
    )
    return [
        ChannelRead(
            id=int(row["id"]),
            guild_id=int(row["guild_id"]),
            name=str(row["name"]),
            type=int(row["type"]),
            position=int(row["position"]),
        )
        for row in rows
    ]


async def read_guild(guild_row: Any, user_id: int) -> GuildRead:
    guild_id = int(guild_row["id"])
    owner_id = int(guild_row["owner_id"])
    return GuildRead(
        id=guild_id,
        name=str(guild_row["name"]),
        owner_id=owner_id,
        permissions=await permissions_for_member(guild_id, user_id, owner_id),
        channels=await list_channels(guild_id),
        roles=await list_roles(guild_id),
        members=await list_members(guild_id, owner_id),
        messages=await list_messages(guild_id),
    )


async def list_roles(guild_id: int) -> list[RoleRead]:
    rows = await database.fetch(
        """
        SELECT id, guild_id, name, permissions, position
        FROM roles
        WHERE guild_id = $1
        ORDER BY position ASC, id ASC
        """,
        guild_id,
    )
    return [
        RoleRead(
            id=int(row["id"]),
            guild_id=int(row["guild_id"]),
            name=str(row["name"]),
            permissions=int(row["permissions"]),
            position=int(row["position"]),
        )
        for row in rows
    ]


async def list_members(guild_id: int, owner_id: int) -> list[MemberRead]:
    rows = await database.fetch(
        """
        SELECT u.id, u.username, u.status
        FROM users u
        JOIN guild_members gm ON gm.user_id = u.id
        WHERE gm.guild_id = $1
        ORDER BY u.username ASC
        """,
        guild_id,
    )
    role_rows = await database.fetch(
        """
        SELECT mr.user_id, r.id, r.name
        FROM member_roles mr
        JOIN roles r ON r.id = mr.role_id
        WHERE mr.guild_id = $1
        ORDER BY r.position ASC, r.id ASC
        """,
        guild_id,
    )
    roles_by_user: dict[int, list[tuple[int, str]]] = {}
    for row in role_rows:
        roles_by_user.setdefault(int(row["user_id"]), []).append((int(row["id"]), str(row["name"])))
    return [
        MemberRead(
            id=int(row["id"]),
            username=str(row["username"]),
            status=int(row["status"]),
            role=member_role_label(
                int(row["id"]),
                owner_id,
                roles_by_user.get(int(row["id"]), []),
            ),
            role_ids=[role_id for role_id, _ in roles_by_user.get(int(row["id"]), [])],
        )
        for row in rows
    ]


async def list_messages(guild_id: int) -> list[MessageRead]:
    rows = await database.fetch(
        """
        SELECT m.id, m.channel_id, m.author_id, u.username AS author_name, m.content
        FROM messages m
        JOIN channels c ON c.id = m.channel_id
        JOIN users u ON u.id = m.author_id
        WHERE c.guild_id = $1
        ORDER BY m.id ASC
        LIMIT 200
        """,
        guild_id,
    )
    return [
        MessageRead(
            id=int(row["id"]),
            channel_id=int(row["channel_id"]),
            author_id=int(row["author_id"]),
            author_name=str(row["author_name"]),
            content=str(row["content"]),
        )
        for row in rows
    ]


async def permissions_for_member(guild_id: int, user_id: int, owner_id: int) -> int:
    membership = await database.fetchrow(
        """
        SELECT 1
        FROM guild_members
        WHERE guild_id = $1 AND user_id = $2
        """,
        guild_id,
        user_id,
    )
    if membership is None:
        return 0
    if user_id == owner_id:
        return ALL_PERMISSIONS

    role_rows = await database.fetch(
        """
        SELECT r.permissions
        FROM roles r
        JOIN member_roles mr ON mr.role_id = r.id
        WHERE mr.guild_id = $1 AND mr.user_id = $2
        """,
        guild_id,
        user_id,
    )
    role_permissions = [int(row["permissions"]) for row in role_rows]
    return merge_permissions([BASE_MEMBER_PERMISSIONS, *role_permissions])


async def get_manageable_guild_row(guild_id: int, actor: UserPublic) -> Any:
    guild_row = await database.fetchrow(
        "SELECT id, name, owner_id FROM guilds WHERE id = $1",
        guild_id,
    )
    if guild_row is None:
        raise KeyError(guild_id)

    permissions = await permissions_for_member(
        guild_id,
        actor.id,
        int(guild_row["owner_id"]),
    )
    if not has_permission(permissions, Permission.ADMINISTRATOR):
        raise PermissionError("administrator permission required")
    return guild_row


async def require_member_and_role(guild_id: int, member_id: int, role_id: int) -> None:
    member_row = await database.fetchrow(
        """
        SELECT 1
        FROM guild_members
        WHERE guild_id = $1 AND user_id = $2
        """,
        guild_id,
        member_id,
    )
    if member_row is None:
        raise KeyError(member_id)

    role_row = await database.fetchrow(
        """
        SELECT 1
        FROM roles
        WHERE guild_id = $1 AND id = $2
        """,
        guild_id,
        role_id,
    )
    if role_row is None:
        raise KeyError(role_id)


def member_role_label(user_id: int, owner_id: int, roles: list[tuple[int, str]]) -> str:
    if user_id == owner_id:
        return "Owner"
    if roles:
        return ", ".join(name for _, name in roles)
    return "Member"
