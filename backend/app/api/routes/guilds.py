from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.schemas.auth import UserPublic
from app.schemas.guild import ChannelCreate, ChannelRead, GuildCreate, GuildRead
from app.services.guild_service import create_channel, create_guild, list_guilds_for_user

router = APIRouter()


@router.get("/me", response_model=list[GuildRead])
async def list_my_guilds(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> list[GuildRead]:
    return await list_guilds_for_user(current_user)


@router.post("", response_model=GuildRead, status_code=status.HTTP_201_CREATED)
async def create_user_guild(
    payload: GuildCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> GuildRead:
    return await create_guild(payload, current_user)


@router.post(
    "/{guild_id}/channels",
    response_model=ChannelRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_guild_channel(
    guild_id: int,
    payload: ChannelCreate,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> ChannelRead:
    try:
        return await create_channel(guild_id, payload, current_user)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="guild not found",
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="manage channels permission required",
        ) from exc
