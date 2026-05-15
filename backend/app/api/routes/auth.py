from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.schemas.auth import AuthRequest, AuthResponse, UserPublic
from app.services.auth_service import (
    AuthServiceUnavailableError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    login_user,
    register_user,
)

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: AuthRequest) -> AuthResponse:
    try:
        return await register_user(payload)
    except DuplicateUsernameError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already exists",
        ) from exc
    except AuthServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database is required for registration",
        ) from exc


@router.post("/login", response_model=AuthResponse)
async def login(payload: AuthRequest) -> AuthResponse:
    try:
        return await login_user(payload)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except AuthServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database is required for login",
        ) from exc


@router.get("/me", response_model=UserPublic)
async def read_current_user(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
) -> UserPublic:
    return current_user
