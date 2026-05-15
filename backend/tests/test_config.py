from app.core.config import Settings


def test_cors_origins_parse_comma_separated_env_value() -> None:
    settings = Settings(CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173")

    assert settings.cors_origin_list == ["http://localhost:5173", "http://127.0.0.1:5173"]


def test_webrtc_ice_servers_filter_invalid_entries_and_detect_turn() -> None:
    settings = Settings(
        WEBRTC_ICE_SERVERS_JSON=(
            '[{"urls":"stun:stun.l.google.com:19302"},'
            '{"urls":["turn:turn.example.com:3478"],"username":"user","credential":"secret"},'
            '{"username":"missing-urls"}]'
        ),
    )

    assert len(settings.webrtc_ice_servers) == 2
    assert settings.webrtc_turn_configured is True


def test_channel_names_use_ascii_slug_format() -> None:
    from pydantic import ValidationError

    from app.schemas.guild import ChannelCreate

    ChannelCreate(name="ui-room", type=0)

    try:
        ChannelCreate(name="잘못된채널", type=0)
    except ValidationError:
        return

    raise AssertionError("expected non-ascii channel name validation error")
