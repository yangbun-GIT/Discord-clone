from fastapi import APIRouter

from app.api.routes import auth, channels, dev, dms, guilds, health, meta, store, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dev.router, prefix="/dev", tags=["dev"])
api_router.include_router(guilds.router, prefix="/guilds", tags=["guilds"])
api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dms.router, prefix="/dms", tags=["dms"])
api_router.include_router(store.router, prefix="/store", tags=["store"])
