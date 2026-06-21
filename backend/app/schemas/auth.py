from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    id: int
    username: str
    status: int


class AuthRequest(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    )
    password: str = Field(min_length=8, max_length=128)


class DevSessionRequest(BaseModel):
    username: str = Field(default="admin", min_length=2, max_length=32)
    user_id: int = 42


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class DevSessionResponse(AuthResponse):
    pass
