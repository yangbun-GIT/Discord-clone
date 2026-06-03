from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.schemas.auth import UserPublic
from app.schemas.dm import DmCreate, DmMessageCreate, DmMessageRead, DmRead
from app.services.dm_service import create_dm, create_dm_message, list_dms

router = APIRouter()


@router.get("", response_model=list[DmRead])
async def list_my_dms(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> list[DmRead]:
    return await list_dms(current_user)


@router.post("", response_model=DmRead, status_code=status.HTTP_201_CREATED)
async def create_direct_message(
    payload: DmCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> DmRead:
    try:
        return await create_dm(payload, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="recipient not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{dm_id}/messages",
    response_model=DmMessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_direct_message_message(
    dm_id: int,
    payload: DmMessageCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> DmMessageRead:
    if payload.dm_id != dm_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dm_id in path and payload must match",
        )

    try:
        return await create_dm_message(dm_id=dm_id, payload=payload, author=current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="direct message not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="direct message membership required",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
