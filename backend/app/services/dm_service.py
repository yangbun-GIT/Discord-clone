from app.schemas.auth import UserPublic
from app.schemas.dm import DmCreate, DmMessageCreate, DmMessageRead, DmRead, RelationshipRead
from app.services.dm_storage import get_dm_storage


async def list_relationships(user: UserPublic) -> list[RelationshipRead]:
    return await get_dm_storage().list_relationships(user)


async def list_dms(user: UserPublic) -> list[DmRead]:
    return await get_dm_storage().list_dms(user)


async def create_dm(payload: DmCreate, user: UserPublic) -> DmRead:
    return await get_dm_storage().create_dm(payload, user)


async def create_dm_message(
    *,
    dm_id: int,
    payload: DmMessageCreate,
    author: UserPublic,
) -> DmMessageRead:
    return await get_dm_storage().create_dm_message(dm_id=dm_id, payload=payload, author=author)
