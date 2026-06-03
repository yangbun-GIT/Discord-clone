from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.schemas.auth import UserPublic
from app.schemas.dm import RelationshipRead
from app.services.dm_service import list_relationships

router = APIRouter()


@router.get("/me/relationships", response_model=list[RelationshipRead])
async def list_my_relationships(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> list[RelationshipRead]:
    return await list_relationships(current_user)
