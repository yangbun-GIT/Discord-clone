from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    id: int
    username: str
    status: int


class DevSessionRequest(BaseModel):
    username: str = Field(default="yangbun", min_length=2, max_length=32)
    user_id: int = 42


class DevSessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic

