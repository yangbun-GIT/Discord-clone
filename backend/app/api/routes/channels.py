from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.demo.store import demo_store
from app.schemas.auth import UserPublic
from app.schemas.guild import MessageRead
from app.schemas.message import MessageCreate

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
        return demo_store.create_message(
            channel_id=channel_id,
            author_id=current_user.id,
            author_name=current_user.username,
            content=payload.content,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="channel not found",
        ) from exc
