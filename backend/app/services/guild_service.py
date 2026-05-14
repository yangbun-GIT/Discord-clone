from app.db.pool import database
from app.demo.store import demo_store
from app.repositories.guilds import guild_repository
from app.schemas.auth import UserPublic
from app.schemas.guild import ChannelCreate, ChannelRead, GuildRead, MessageRead


async def list_guilds_for_user(user: UserPublic | None = None) -> list[GuildRead]:
    if database.is_connected:
        user_id = user.id if user else 42
        return await guild_repository.list_for_user(user_id)
    return demo_store.list_guilds()


async def create_channel(
    guild_id: int,
    payload: ChannelCreate,
) -> ChannelRead:
    if database.is_connected:
        return await guild_repository.create_channel(guild_id, payload)
    return demo_store.create_channel(guild_id, payload)


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
