from fastapi import APIRouter

from app.core.config import get_settings
from app.db.pool import database
from app.realtime.redis_bus import redis_bus

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "database": {
            "configured": bool(settings.database_url),
            "connected": database.is_connected,
        },
        "redis": {
            "configured": bool(settings.redis_url),
            "connected": redis_bus.is_connected,
        },
    }
