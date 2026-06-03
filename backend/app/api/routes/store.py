from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.schemas.auth import UserPublic
from app.schemas.store import StoreCatalogRead, StoreItemDetailRead
from app.services.store_service import get_store_catalog, get_store_item_detail

router = APIRouter()


@router.get("/catalog", response_model=StoreCatalogRead)
async def read_store_catalog(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> StoreCatalogRead:
    return await get_store_catalog(current_user)


@router.get("/items/{item_id}", response_model=StoreItemDetailRead)
async def read_store_item_detail(
    item_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> StoreItemDetailRead:
    try:
        return await get_store_item_detail(item_id, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="store item not found",
        ) from exc
