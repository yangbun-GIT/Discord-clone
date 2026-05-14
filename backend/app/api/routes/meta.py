from fastapi import APIRouter

from app.domain.permissions import Permission

router = APIRouter()


@router.get("/permissions")
async def list_permissions() -> dict[str, int]:
    return {permission.name: permission.value for permission in Permission}

