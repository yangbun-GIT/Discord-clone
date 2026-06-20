from app.schemas.auth import UserPublic
from app.schemas.dm import (
    DmCreate,
    DmDeleteRead,
    DmMessageCreate,
    DmMessageDeleteRead,
    DmMessageRead,
    DmRead,
    PresenceUpdateRead,
    RelationshipDeleteRead,
    RelationshipRead,
    UserPresenceStatus,
)
from app.services.dm_storage import get_dm_storage


async def list_relationships(user: UserPublic) -> list[RelationshipRead]:
    return await get_dm_storage().list_relationships(user)


async def update_presence(
    *,
    user: UserPublic,
    status: UserPresenceStatus,
    activity: str | None,
) -> tuple[PresenceUpdateRead, list[int]]:
    return await get_dm_storage().update_presence(user=user, status=status, activity=activity)


async def send_friend_request(
    *,
    actor: UserPublic,
    target_username: str,
) -> tuple[RelationshipRead, RelationshipRead]:
    return await get_dm_storage().send_friend_request(actor=actor, target_username=target_username)


async def accept_friend_request(
    *,
    actor: UserPublic,
    target_user_id: int,
) -> tuple[RelationshipRead, RelationshipRead]:
    return await get_dm_storage().accept_friend_request(actor=actor, target_user_id=target_user_id)


async def reject_friend_request(
    *,
    actor: UserPublic,
    target_user_id: int,
) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
    return await get_dm_storage().reject_friend_request(actor=actor, target_user_id=target_user_id)


async def cancel_friend_request(
    *,
    actor: UserPublic,
    target_user_id: int,
) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
    return await get_dm_storage().cancel_friend_request(actor=actor, target_user_id=target_user_id)


async def remove_friend(
    *,
    actor: UserPublic,
    target_user_id: int,
) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
    return await get_dm_storage().remove_friend(actor=actor, target_user_id=target_user_id)


async def block_user(
    *,
    actor: UserPublic,
    target_user_id: int,
) -> tuple[RelationshipRead, RelationshipDeleteRead]:
    return await get_dm_storage().block_user(actor=actor, target_user_id=target_user_id)


async def unblock_user(
    *,
    actor: UserPublic,
    target_user_id: int,
) -> tuple[RelationshipDeleteRead, RelationshipDeleteRead]:
    return await get_dm_storage().unblock_user(actor=actor, target_user_id=target_user_id)


async def list_dms(user: UserPublic) -> list[DmRead]:
    return await get_dm_storage().list_dms(user)


async def create_dm(payload: DmCreate, user: UserPublic) -> DmRead:
    return await get_dm_storage().create_dm(payload, user)


async def close_dm(*, dm_id: int, actor: UserPublic) -> DmDeleteRead:
    return await get_dm_storage().close_dm(dm_id=dm_id, actor=actor)


async def create_dm_message(
    *,
    dm_id: int,
    payload: DmMessageCreate,
    author: UserPublic,
) -> DmMessageRead:
    return await get_dm_storage().create_dm_message(dm_id=dm_id, payload=payload, author=author)


async def delete_dm_message(
    *,
    dm_id: int,
    message_id: int,
    actor: UserPublic,
) -> DmMessageDeleteRead:
    return await get_dm_storage().delete_dm_message(dm_id=dm_id, message_id=message_id, actor=actor)
