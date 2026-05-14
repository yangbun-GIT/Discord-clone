from fastapi import APIRouter

from app.demo.data import demo_guilds
from app.schemas.guild import GuildRead

router = APIRouter()


@router.get("/me", response_model=list[GuildRead])
async def list_my_guilds() -> list[GuildRead]:
    return demo_guilds()

