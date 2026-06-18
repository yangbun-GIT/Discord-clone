from __future__ import annotations

from app.repositories.guilds import guild_repository
from app.schemas.auth import UserPublic
from app.schemas.guild import GuildRead, MemberRoleUpdate, RoleCreate


class RoleRepository:
    async def create_role(
        self,
        guild_id: int,
        payload: RoleCreate,
        actor: UserPublic,
    ) -> GuildRead:
        return await guild_repository.create_role(guild_id, payload, actor)

    async def assign_member_role(
        self,
        guild_id: int,
        member_id: int,
        payload: MemberRoleUpdate,
        actor: UserPublic,
    ) -> GuildRead:
        return await guild_repository.assign_member_role(guild_id, member_id, payload, actor)

    async def remove_member_role(
        self,
        guild_id: int,
        member_id: int,
        role_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        return await guild_repository.remove_member_role(guild_id, member_id, role_id, actor)


role_repository = RoleRepository()
