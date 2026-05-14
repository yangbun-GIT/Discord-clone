from app.core.config import Settings


def test_cors_origins_parse_comma_separated_env_value() -> None:
    settings = Settings(CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173")

    assert settings.cors_origin_list == ["http://localhost:5173", "http://127.0.0.1:5173"]


def test_channel_names_use_ascii_slug_format() -> None:
    from pydantic import ValidationError

    from app.schemas.guild import ChannelCreate

    ChannelCreate(name="ui-room", type=0)

    try:
        ChannelCreate(name="잘못된채널", type=0)
    except ValidationError:
        return

    raise AssertionError("expected non-ascii channel name validation error")
