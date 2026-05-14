from app.core.config import Settings


def test_cors_origins_parse_comma_separated_env_value() -> None:
    settings = Settings(CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173")

    assert settings.cors_origin_list == ["http://localhost:5173", "http://127.0.0.1:5173"]
