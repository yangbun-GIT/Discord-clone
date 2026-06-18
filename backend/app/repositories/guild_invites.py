from __future__ import annotations

import secrets

from app.db.pool import database
from app.domain.permissions import Permission, has_permission
from app.repositories.guild_common import ensure_user, permissions_for_member
from app.schemas.auth import UserPublic
from app.schemas.guild import GuildRead, InviteRead


class InviteRepository:
    async def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead:
        guild_row = await database.fetchrow(
            "SELECT id, owner_id FROM guilds WHERE id = $1",
            guild_id,
        )
        if guild_row is None:
            raise KeyError(guild_id)

        permissions = await permissions_for_member(guild_id, actor.id, int(guild_row["owner_id"]))
        if not has_permission(permissions, Permission.CREATE_INSTANT_INVITE):
            raise PermissionError("create invite permission required")

        for _ in range(5):
            code = secrets.token_urlsafe(8)
            result = await database.execute(
                """
                INSERT INTO invites (code, guild_id, creator_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (code) DO NOTHING
                """,
                code,
                guild_id,
                actor.id,
            )
            if result == "INSERT 0 1":
                return InviteRead(code=code, guild_id=guild_id, created_by=actor.id)
        raise RuntimeError("could not create unique invite code")

    async def join_invite(self, code: str, user: UserPublic) -> GuildRead:
        from app.repositories.guilds import guild_repository

        invite_row = await database.fetchrow(
            """
            SELECT guild_id
            FROM invites
            WHERE code = $1
            """,
            code,
        )
        if invite_row is None:
            raise KeyError(code)

        await ensure_user(user)
        await database.execute(
            """
            INSERT INTO guild_members (guild_id, user_id)
            VALUES ($1, $2)
            ON CONFLICT (guild_id, user_id) DO NOTHING
            """,
            int(invite_row["guild_id"]),
            user.id,
        )
        guild = await guild_repository.get_for_user(int(invite_row["guild_id"]), user.id)
        if guild is None:
            raise KeyError(code)
        return guild


invite_repository = InviteRepository()
