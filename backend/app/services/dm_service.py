from app.db.pool import database
from app.demo.store import demo_store
from app.repositories.dms import dm_repository
from app.schemas.auth import UserPublic
from app.schemas.dm import DmCreate, DmMessageCreate, DmMessageRead, DmRead, RelationshipRead


async def list_relationships(user: UserPublic) -> list[RelationshipRead]:
    if database.is_connected:
        return await dm_repository.list_relationships(user.id)
    return demo_store.list_relationships(user.id)


async def list_dms(user: UserPublic) -> list[DmRead]:
    if database.is_connected:
        return await dm_repository.list_dms(user)
    return demo_store.list_dms(user)


async def create_dm(payload: DmCreate, user: UserPublic) -> DmRead:
    if database.is_connected:
        return await dm_repository.create_dm(payload, user)
    return demo_store.create_dm(payload, user)


async def create_dm_message(
    *,
    dm_id: int,
    payload: DmMessageCreate,
    author: UserPublic,
) -> DmMessageRead:
    if database.is_connected:
        return await dm_repository.create_dm_message(dm_id=dm_id, payload=payload, author=author)
    return demo_store.create_dm_message(dm_id=dm_id, payload=payload, author=author)
