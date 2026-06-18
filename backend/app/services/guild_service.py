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
from app.services.guild_storage import get_guild_storage


async def list_guilds_for_user(user: UserPublic | None = None) -> list[GuildRead]:
    return await get_guild_storage().list_guilds_for_user(user)


async def get_guild_for_user(guild_id: int, user: UserPublic) -> GuildRead:
    return await get_guild_storage().get_guild_for_user(guild_id, user)


async def create_guild(payload: GuildCreate, owner: UserPublic) -> GuildRead:
    return await get_guild_storage().create_guild(payload, owner)


async def create_invite(guild_id: int, actor: UserPublic) -> InviteRead:
    return await get_guild_storage().create_invite(guild_id, actor)


async def join_invite(code: str, user: UserPublic) -> GuildRead:
    return await get_guild_storage().join_invite(code, user)


async def create_role(guild_id: int, payload: RoleCreate, actor: UserPublic) -> GuildRead:
    return await get_guild_storage().create_role(guild_id, payload, actor)


async def assign_member_role(
    guild_id: int,
    member_id: int,
    payload: MemberRoleUpdate,
    actor: UserPublic,
) -> GuildRead:
    return await get_guild_storage().assign_member_role(guild_id, member_id, payload, actor)


async def remove_member_role(
    guild_id: int,
    member_id: int,
    role_id: int,
    actor: UserPublic,
) -> GuildRead:
    return await get_guild_storage().remove_member_role(guild_id, member_id, role_id, actor)


async def remove_member(guild_id: int, member_id: int, actor: UserPublic) -> GuildRead:
    return await get_guild_storage().remove_member(guild_id, member_id, actor)


async def create_channel(
    guild_id: int,
    payload: ChannelCreate,
    actor: UserPublic,
) -> ChannelRead:
    return await get_guild_storage().create_channel(guild_id, payload, actor)


async def create_message(
    *,
    channel_id: int,
    author: UserPublic,
    content: str,
) -> MessageRead:
    return await get_guild_storage().create_message(
        channel_id=channel_id,
        author=author,
        content=content,
    )


async def update_message(
    *,
    channel_id: int,
    message_id: int,
    actor: UserPublic,
    content: str,
) -> MessageRead:
    return await get_guild_storage().update_message(
        channel_id=channel_id,
        message_id=message_id,
        actor=actor,
        content=content,
    )


async def delete_message(
    *,
    channel_id: int,
    message_id: int,
    actor: UserPublic,
) -> MessageDeleteRead:
    return await get_guild_storage().delete_message(
        channel_id=channel_id,
        message_id=message_id,
        actor=actor,
    )
