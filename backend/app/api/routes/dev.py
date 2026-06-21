from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.auth import DevSessionRequest, DevSessionResponse, UserPublic
from app.services.dm_service import reset_development_workspace

router = APIRouter()


@router.post("/session", response_model=DevSessionResponse)
async def create_dev_session(payload: DevSessionRequest) -> DevSessionResponse:
    settings = get_settings()
    if settings.environment not in {"local", "dev", "test"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user = UserPublic(id=payload.user_id, username=payload.username, status=1)
    token = create_access_token(subject=str(user.id), claims={"username": user.username})
    return DevSessionResponse(access_token=token, user=user)


@router.post("/session/reset")
async def reset_dev_session(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> dict[str, bool]:
    settings = get_settings()
    if settings.environment not in {"local", "dev", "test"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        await reset_development_workspace(current_user)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    return {"reset": True}
