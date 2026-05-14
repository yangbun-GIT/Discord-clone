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
            "configured": settings.database_url is not None,
            "connected": database.is_connected,
        },
        "redis": {
            "configured": settings.redis_url is not None,
            "connected": redis_bus.is_connected,
        },
    }

