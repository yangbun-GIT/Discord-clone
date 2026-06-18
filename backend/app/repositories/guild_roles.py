from __future__ import annotations

from app.db.pool import database
from app.repositories.guild_common import (
    get_manageable_guild_row,
    id_generator,
    read_guild,
    require_member_and_role,
)
from app.schemas.auth import UserPublic
from app.schemas.guild import GuildRead, MemberRoleUpdate, RoleCreate, RoleRead


class RoleRepository:
    async def create_role(
        self,
        guild_id: int,
        payload: RoleCreate,
        actor: UserPublic,
    ) -> GuildRead:
        guild_row = await get_manageable_guild_row(guild_id, actor)
        position_row = await database.fetchrow(
            """
            SELECT COALESCE(MAX(position), -1) + 1 AS next_position
            FROM roles
            WHERE guild_id = $1
            """,
            guild_id,
        )
        role = RoleRead(
            id=id_generator.generate(),
            guild_id=guild_id,
            name=payload.name,
            permissions=payload.permissions,
            position=int(position_row["next_position"]) if position_row else 0,
        )
        await database.execute(
            """
            INSERT INTO roles (id, guild_id, name, permissions, position)
            VALUES ($1, $2, $3, $4, $5)
            """,
            role.id,
            role.guild_id,
            role.name,
            role.permissions,
            role.position,
        )
        return await read_guild(guild_row, actor.id)

    async def assign_member_role(
        self,
        guild_id: int,
        member_id: int,
        payload: MemberRoleUpdate,
        actor: UserPublic,
    ) -> GuildRead:
        guild_row = await get_manageable_guild_row(guild_id, actor)
        await require_member_and_role(guild_id, member_id, payload.role_id)
        await database.execute(
            """
            INSERT INTO member_roles (guild_id, user_id, role_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (guild_id, user_id, role_id) DO NOTHING
            """,
            guild_id,
            member_id,
            payload.role_id,
        )
        return await read_guild(guild_row, actor.id)

    async def remove_member_role(
        self,
        guild_id: int,
        member_id: int,
        role_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        guild_row = await get_manageable_guild_row(guild_id, actor)
        await require_member_and_role(guild_id, member_id, role_id)
        await database.execute(
            """
            DELETE FROM member_roles
            WHERE guild_id = $1 AND user_id = $2 AND role_id = $3
            """,
            guild_id,
            member_id,
            role_id,
        )
        return await read_guild(guild_row, actor.id)


role_repository = RoleRepository()
