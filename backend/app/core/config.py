import json
from functools import lru_cache
from typing import Any

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
    webrtc_ice_servers_json: str = Field(
        default='[{"urls":"stun:stun.l.google.com:19302"}]',
        validation_alias="WEBRTC_ICE_SERVERS_JSON",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def webrtc_ice_servers(self) -> list[dict[str, Any]]:
        parsed = json.loads(self.webrtc_ice_servers_json)
        if not isinstance(parsed, list):
            raise ValueError("WEBRTC_ICE_SERVERS_JSON must be a JSON array")
        return [item for item in parsed if self._is_valid_ice_server(item)]

    @property
    def webrtc_turn_configured(self) -> bool:
        for server in self.webrtc_ice_servers:
            urls = server["urls"]
            url_values = urls if isinstance(urls, list) else [urls]
            if any(url.startswith(("turn:", "turns:")) for url in url_values):
                return True
        return False

    @property
    def webrtc_stun_configured(self) -> bool:
        for server in self.webrtc_ice_servers:
            urls = server["urls"]
            url_values = urls if isinstance(urls, list) else [urls]
            if any(url.startswith("stun:") for url in url_values):
                return True
        return False

    @staticmethod
    def _is_valid_ice_server(item: object) -> bool:
        if not isinstance(item, dict):
            return False
        urls = item.get("urls")
        if isinstance(urls, str):
            return bool(urls.strip())
        if isinstance(urls, list):
            return any(isinstance(url, str) and url.strip() for url in urls)
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()
