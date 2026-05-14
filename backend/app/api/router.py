from fastapi import APIRouter

from app.api.routes import dev, guilds, health, meta

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])
api_router.include_router(dev.router, prefix="/dev", tags=["dev"])
api_router.include_router(guilds.router, prefix="/guilds", tags=["guilds"])

