from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.api.errors import raise_route_error
from app.core.operation_limits import MESSAGE_CREATE_LIMIT, require_rest_operation
from app.realtime.publisher import publish_dm_create, publish_dm_message_create
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
        dm = await create_dm(payload, current_user)
        await publish_dm_create(dm)
        return dm
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="recipient not found",
            forbidden=str(exc),
            bad_request=str(exc),
        )


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
    await require_rest_operation(
        f"dm-message-create:{current_user.id}:{dm_id}",
        MESSAGE_CREATE_LIMIT,
    )
    if payload.dm_id != dm_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dm_id in path and payload must match",
        )

    try:
        message = await create_dm_message(dm_id=dm_id, payload=payload, author=current_user)
        await publish_dm_message_create(message)
        return message
    except (KeyError, PermissionError, ValueError) as exc:
        raise_route_error(
            exc,
            not_found="direct message not found",
            forbidden="direct message membership required",
            bad_request=str(exc),
        )
