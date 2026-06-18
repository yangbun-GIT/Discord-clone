from __future__ import annotations

from typing import Protocol

from app.db.pool import database
from app.demo.store import demo_store
from app.repositories.guild_channels import channel_repository
from app.repositories.guild_invites import invite_repository
from app.repositories.guild_members import member_repository
from app.repositories.guild_messages import message_repository
from app.repositories.guild_roles import role_repository
from app.repositories.guilds import guild_repository
from app.schemas.auth import UserPublic
from app.schemas.guild import (
    ChannelCreate,
    ChannelRead,
    GuildCreate,
    GuildRead,
    InviteRead,
    MemberRoleUpdate,
    MessageRead,
    RoleCreate,
)
from app.schemas.message import MessageDeleteRead


class GuildReadStorage(Protocol):
    async def list_guilds_for_user(self, user: UserPublic | None = None) -> list[GuildRead]: ...

    async def get_guild_for_user(self, guild_id: int, user: UserPublic) -> GuildRead: ...

    async def create_guild(self, payload: GuildCreate, owner: UserPublic) -> GuildRead: ...


class GuildInviteStorage(Protocol):
    async def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead: ...

    async def join_invite(self, code: str, user: UserPublic) -> GuildRead: ...


class GuildRoleStorage(Protocol):
    async def create_role(
        self,
        guild_id: int,
        payload: RoleCreate,
        actor: UserPublic,
    ) -> GuildRead: ...

    async def assign_member_role(
        self,
        guild_id: int,
        member_id: int,
        payload: MemberRoleUpdate,
        actor: UserPublic,
    ) -> GuildRead: ...

    async def remove_member_role(
        self,
        guild_id: int,
        member_id: int,
        role_id: int,
        actor: UserPublic,
    ) -> GuildRead: ...


class GuildMemberStorage(Protocol):
    async def remove_member(
        self,
        guild_id: int,
        member_id: int,
        actor: UserPublic,
    ) -> GuildRead: ...


class GuildChannelStorage(Protocol):
    async def create_channel(
        self,
        guild_id: int,
        payload: ChannelCreate,
        actor: UserPublic,
    ) -> ChannelRead: ...


class GuildMessageStorage(Protocol):
    async def create_message(
        self,
        *,
        channel_id: int,
        author: UserPublic,
        content: str,
    ) -> MessageRead: ...

    async def update_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
        content: str,
    ) -> MessageRead: ...

    async def delete_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> MessageDeleteRead: ...


class GuildStorage(
    GuildReadStorage,
    GuildInviteStorage,
    GuildRoleStorage,
    GuildMemberStorage,
    GuildChannelStorage,
    GuildMessageStorage,
    Protocol,
):
    pass


class PostgresGuildStorage:
    async def list_guilds_for_user(self, user: UserPublic | None = None) -> list[GuildRead]:
        if user is None:
            return []
        return await guild_repository.list_for_user(user.id)

    async def get_guild_for_user(self, guild_id: int, user: UserPublic) -> GuildRead:
        guild = await guild_repository.get_for_user(guild_id, user.id)
        if guild is None:
            raise KeyError(guild_id)
        return guild

    async def create_guild(self, payload: GuildCreate, owner: UserPublic) -> GuildRead:
        return await guild_repository.create_guild(payload, owner)

    async def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead:
        return await invite_repository.create_invite(guild_id, actor)

    async def join_invite(self, code: str, user: UserPublic) -> GuildRead:
        return await invite_repository.join_invite(code, user)

    async def create_role(
        self,
        guild_id: int,
        payload: RoleCreate,
        actor: UserPublic,
    ) -> GuildRead:
        return await role_repository.create_role(guild_id, payload, actor)

    async def assign_member_role(
        self,
        guild_id: int,
        member_id: int,
        payload: MemberRoleUpdate,
        actor: UserPublic,
    ) -> GuildRead:
        return await role_repository.assign_member_role(guild_id, member_id, payload, actor)

    async def remove_member_role(
        self,
        guild_id: int,
        member_id: int,
        role_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        return await role_repository.remove_member_role(guild_id, member_id, role_id, actor)

    async def remove_member(
        self,
        guild_id: int,
        member_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        return await member_repository.remove_member(guild_id, member_id, actor)

    async def create_channel(
        self,
        guild_id: int,
        payload: ChannelCreate,
        actor: UserPublic,
    ) -> ChannelRead:
        return await channel_repository.create_channel(guild_id, payload, actor)

    async def create_message(
        self,
        *,
        channel_id: int,
        author: UserPublic,
        content: str,
    ) -> MessageRead:
        return await message_repository.create_message(
            channel_id=channel_id,
            author=author,
            content=content,
        )

    async def update_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
        content: str,
    ) -> MessageRead:
        return await message_repository.update_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=actor,
            content=content,
        )

    async def delete_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> MessageDeleteRead:
        return await message_repository.delete_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=actor,
        )


class DemoGuildStorage:
    async def list_guilds_for_user(self, user: UserPublic | None = None) -> list[GuildRead]:
        return demo_store.list_guilds(user.id if user else None)

    async def get_guild_for_user(self, guild_id: int, user: UserPublic) -> GuildRead:
        return demo_store.get_guild_for_user(guild_id, user)

    async def create_guild(self, payload: GuildCreate, owner: UserPublic) -> GuildRead:
        return demo_store.create_guild(payload, owner)

    async def create_invite(self, guild_id: int, actor: UserPublic) -> InviteRead:
        return demo_store.create_invite(guild_id, actor)

    async def join_invite(self, code: str, user: UserPublic) -> GuildRead:
        return demo_store.join_invite(code, user)

    async def create_role(
        self,
        guild_id: int,
        payload: RoleCreate,
        actor: UserPublic,
    ) -> GuildRead:
        return demo_store.create_role(guild_id, payload, actor)

    async def assign_member_role(
        self,
        guild_id: int,
        member_id: int,
        payload: MemberRoleUpdate,
        actor: UserPublic,
    ) -> GuildRead:
        return demo_store.assign_member_role(guild_id, member_id, payload, actor)

    async def remove_member_role(
        self,
        guild_id: int,
        member_id: int,
        role_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        return demo_store.remove_member_role(guild_id, member_id, role_id, actor)

    async def remove_member(
        self,
        guild_id: int,
        member_id: int,
        actor: UserPublic,
    ) -> GuildRead:
        return demo_store.remove_member(guild_id, member_id, actor)

    async def create_channel(
        self,
        guild_id: int,
        payload: ChannelCreate,
        actor: UserPublic,
    ) -> ChannelRead:
        return demo_store.create_channel(guild_id, payload, actor)

    async def create_message(
        self,
        *,
        channel_id: int,
        author: UserPublic,
        content: str,
    ) -> MessageRead:
        return demo_store.create_message(
            channel_id=channel_id,
            author_id=author.id,
            author_name=author.username,
            content=content,
        )

    async def update_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
        content: str,
    ) -> MessageRead:
        return demo_store.update_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=actor,
            content=content,
        )

    async def delete_message(
        self,
        *,
        channel_id: int,
        message_id: int,
        actor: UserPublic,
    ) -> MessageDeleteRead:
        return demo_store.delete_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=actor,
        )


postgres_guild_storage = PostgresGuildStorage()
demo_guild_storage = DemoGuildStorage()


def get_guild_storage() -> GuildStorage:
    return postgres_guild_storage if database.is_connected else demo_guild_storage
