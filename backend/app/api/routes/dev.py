from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.auth import DevSessionRequest, DevSessionResponse, UserPublic

router = APIRouter()


@router.post("/session", response_model=DevSessionResponse)
async def create_dev_session(payload: DevSessionRequest) -> DevSessionResponse:
    settings = get_settings()
    if settings.environment not in {"local", "dev", "test"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user = UserPublic(id=payload.user_id, username=payload.username, status=1)
    token = create_access_token(subject=str(user.id), claims={"username": user.username})
    return DevSessionResponse(access_token=token, user=user)

