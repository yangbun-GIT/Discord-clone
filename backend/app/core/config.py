from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Discord Clone API"
    environment: str = Field(default="local", validation_alias="ENVIRONMENT")
    api_prefix: str = "/api"
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="CORS_ORIGINS",
    )

    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    redis_url: str | None = Field(default=None, validation_alias="REDIS_URL")

    jwt_secret: str = Field(
        default="change-this-local-secret-32-bytes-min",
        validation_alias="JWT_SECRET",
    )
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24
    gateway_heartbeat_interval_ms: int = 30_000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
