import asyncio

from app.core.security import create_access_token, hash_password, verify_password
from app.db.pool import database
from app.repositories.users import user_repository
from app.schemas.auth import AuthRequest, AuthResponse, UserPublic


class AuthServiceUnavailableError(RuntimeError):
    pass


class DuplicateUsernameError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


def create_token_response(user: UserPublic) -> AuthResponse:
    token = create_access_token(subject=str(user.id), claims={"username": user.username})
    return AuthResponse(access_token=token, user=user)


async def register_user(payload: AuthRequest) -> AuthResponse:
    if not database.is_connected:
        raise AuthServiceUnavailableError("database is required for registration")

    password_hash = await asyncio.to_thread(hash_password, payload.password)
    try:
        user = await user_repository.create_user(payload.username, password_hash)
    except ValueError as exc:
        raise DuplicateUsernameError("username already exists") from exc
    return create_token_response(user)


async def login_user(payload: AuthRequest) -> AuthResponse:
    if not database.is_connected:
        raise AuthServiceUnavailableError("database is required for login")

    result = await user_repository.get_by_username_with_password(payload.username)
    if result is None:
        raise InvalidCredentialsError("invalid username or password")

    user, password_hash = result
    try:
        password_matches = await asyncio.to_thread(verify_password, payload.password, password_hash)
    except ValueError as exc:
        raise InvalidCredentialsError("invalid username or password") from exc
    if not password_matches:
        raise InvalidCredentialsError("invalid username or password")
    return create_token_response(user)
