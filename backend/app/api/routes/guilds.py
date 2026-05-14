from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.demo.store import demo_store
from app.schemas.auth import UserPublic
from app.schemas.guild import ChannelCreate, ChannelRead, GuildRead

router = APIRouter()


@router.get("/me", response_model=list[GuildRead])
async def list_my_guilds() -> list[GuildRead]:
    return demo_store.list_guilds()


@router.post(
    "/{guild_id}/channels",
    response_model=ChannelRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_guild_channel(
    guild_id: int,
    payload: ChannelCreate,
    _current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> ChannelRead:
    try:
        return demo_store.create_channel(guild_id, payload)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="guild not found",
        ) from exc
