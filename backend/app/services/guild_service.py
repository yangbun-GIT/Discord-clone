from app.db.pool import database
from app.demo.store import demo_store
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


async def list_guilds_for_user(user: UserPublic | None = None) -> list[GuildRead]:
    if database.is_connected:
        if user is None:
            return []
        return await guild_repository.list_for_user(user.id)
    return demo_store.list_guilds(user.id if user else None)


async def create_guild(payload: GuildCreate, owner: UserPublic) -> GuildRead:
    if database.is_connected:
        return await guild_repository.create_guild(payload, owner)
    return demo_store.create_guild(payload, owner)


async def create_invite(guild_id: int, actor: UserPublic) -> InviteRead:
    if database.is_connected:
        return await guild_repository.create_invite(guild_id, actor)
    return demo_store.create_invite(guild_id, actor)


async def join_invite(code: str, user: UserPublic) -> GuildRead:
    if database.is_connected:
        return await guild_repository.join_invite(code, user)
    return demo_store.join_invite(code, user)


async def create_role(guild_id: int, payload: RoleCreate, actor: UserPublic) -> GuildRead:
    if database.is_connected:
        return await guild_repository.create_role(guild_id, payload, actor)
    return demo_store.create_role(guild_id, payload, actor)


async def assign_member_role(
    guild_id: int,
    member_id: int,
    payload: MemberRoleUpdate,
    actor: UserPublic,
) -> GuildRead:
    if database.is_connected:
        return await guild_repository.assign_member_role(guild_id, member_id, payload, actor)
    return demo_store.assign_member_role(guild_id, member_id, payload, actor)


async def remove_member_role(
    guild_id: int,
    member_id: int,
    role_id: int,
    actor: UserPublic,
) -> GuildRead:
    if database.is_connected:
        return await guild_repository.remove_member_role(guild_id, member_id, role_id, actor)
    return demo_store.remove_member_role(guild_id, member_id, role_id, actor)


async def create_channel(
    guild_id: int,
    payload: ChannelCreate,
    actor: UserPublic,
) -> ChannelRead:
    if database.is_connected:
        return await guild_repository.create_channel(guild_id, payload, actor)
    return demo_store.create_channel(guild_id, payload, actor)


async def create_message(
    *,
    channel_id: int,
    author: UserPublic,
    content: str,
) -> MessageRead:
    if database.is_connected:
        return await guild_repository.create_message(
            channel_id=channel_id,
            author=author,
            content=content,
        )
    return demo_store.create_message(
        channel_id=channel_id,
        author_id=author.id,
        author_name=author.username,
        content=content,
    )
