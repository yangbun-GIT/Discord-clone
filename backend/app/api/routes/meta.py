from fastapi import APIRouter

from app.core.config import get_settings
from app.domain.permissions import Permission

router = APIRouter()


@router.get("/permissions")
async def list_permissions() -> dict[str, int]:
    return {permission.name: permission.value for permission in Permission}


@router.get("/voice")
async def get_voice_config() -> dict[str, object]:
    settings = get_settings()
    return {"ice_servers": settings.webrtc_ice_servers}
