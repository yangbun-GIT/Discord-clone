from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.db.pool import database
from app.db.seed import seed_database
from app.gateway.router import gateway_router
from app.realtime.redis_bus import redis_bus


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    await database.connect(settings.database_url)
    if database.is_connected:
        await database.migrate()
        await seed_database()
    await redis_bus.connect(settings.redis_url)
    yield
    await redis_bus.disconnect()
    await database.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)

    app.include_router(api_router, prefix=settings.api_prefix)
    app.include_router(gateway_router)
    return app


app = create_app()
