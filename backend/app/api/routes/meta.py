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
    ice_servers = settings.webrtc_ice_servers
    return {
        "ice_servers": ice_servers,
        "ice_server_count": len(ice_servers),
        "turn_configured": settings.webrtc_turn_configured,
    }
