from typing import NoReturn

from fastapi import HTTPException, status


def raise_route_error(
    exc: Exception,
    *,
    not_found: str | None = None,
    forbidden: str | None = None,
    bad_request: str | None = None,
) -> NoReturn:
    if isinstance(exc, KeyError) and not_found is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=not_found,
        ) from exc
    if isinstance(exc, PermissionError) and forbidden is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=forbidden,
        ) from exc
    if isinstance(exc, ValueError) and bad_request is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=bad_request,
        ) from exc
    raise exc
