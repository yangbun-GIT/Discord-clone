from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.realtime.publisher import (
    publish_message_create,
    publish_message_delete,
    publish_message_update,
)
from app.schemas.auth import UserPublic
from app.schemas.guild import MessageRead
from app.schemas.message import MessageCreate, MessageDeleteRead, MessageUpdate
from app.services.guild_service import create_message, delete_message, update_message

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
        message = await create_message(
            channel_id=channel_id,
            author=current_user,
            content=payload.content,
        )
        await publish_message_create(message)
        return message
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="channel not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="send messages permission required",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{channel_id}/messages/{message_id}",
    response_model=MessageRead,
)
async def update_channel_message(
    channel_id: int,
    message_id: int,
    payload: MessageUpdate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> MessageRead:
    try:
        message = await update_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=current_user,
            content=payload.content,
        )
        await publish_message_update(message)
        return message
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="message not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="message author or manage messages permission required",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{channel_id}/messages/{message_id}",
    response_model=MessageDeleteRead,
)
async def delete_channel_message(
    channel_id: int,
    message_id: int,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> MessageDeleteRead:
    try:
        deleted = await delete_message(
            channel_id=channel_id,
            message_id=message_id,
            actor=current_user,
        )
        await publish_message_delete(deleted)
        return deleted
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="message not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="message author or manage messages permission required",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
