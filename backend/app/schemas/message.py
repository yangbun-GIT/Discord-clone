from pydantic import BaseModel, Field, field_validator

from app.core.sanitize import sanitize_message_content


class MessageCreate(BaseModel):
    channel_id: int
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, value: str) -> str:
        sanitized = sanitize_message_content(value)
        if not sanitized:
            raise ValueError("message content cannot be empty")
        return sanitized


class MessageUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, value: str) -> str:
        sanitized = sanitize_message_content(value)
        if not sanitized:
            raise ValueError("message content cannot be empty")
        return sanitized


class MessageDeleteRead(BaseModel):
    id: int
    channel_id: int
