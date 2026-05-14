from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.schemas.auth import UserPublic
from app.schemas.guild import MessageRead
from app.schemas.message import MessageCreate
from app.services.guild_service import create_message

router = APIRouter()


@router.post(
    "/{channel_id}/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_channel_message(
    channel_id: int,
    payload: MessageCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> MessageRead:
    if payload.channel_id != channel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="channel_id in path and payload must match",
        )

    try:
        return await create_message(
            channel_id=channel_id,
            author=current_user,
            content=payload.content,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="channel not found",
        ) from exc
