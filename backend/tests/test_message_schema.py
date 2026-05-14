import pytest
from pydantic import ValidationError

from app.schemas.message import MessageCreate


def test_message_content_is_sanitized() -> None:
    payload = MessageCreate(channel_id=1, content="<script>alert(1)</script><b>hello</b>")

    assert "<script>" not in payload.content
    assert "&lt;b&gt;hello&lt;/b&gt;" == payload.content


def test_message_content_max_length() -> None:
    with pytest.raises(ValidationError):
        MessageCreate(channel_id=1, content="x" * 2001)

