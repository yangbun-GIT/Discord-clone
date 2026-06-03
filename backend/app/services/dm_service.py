from app.demo.store import demo_store
from app.schemas.auth import UserPublic
from app.schemas.dm import DmCreate, DmMessageCreate, DmMessageRead, DmRead, RelationshipRead


async def list_relationships(user: UserPublic) -> list[RelationshipRead]:
    return demo_store.list_relationships(user.id)


async def list_dms(user: UserPublic) -> list[DmRead]:
    return demo_store.list_dms(user)


async def create_dm(payload: DmCreate, user: UserPublic) -> DmRead:
    return demo_store.create_dm(payload, user)


async def create_dm_message(
    *,
    dm_id: int,
    payload: DmMessageCreate,
    author: UserPublic,
) -> DmMessageRead:
    return demo_store.create_dm_message(dm_id=dm_id, payload=payload, author=author)
