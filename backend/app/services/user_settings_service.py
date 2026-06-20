from app.db.pool import database
from app.demo.store import demo_store
from app.repositories.user_settings import user_settings_repository
from app.schemas.auth import UserPublic
from app.schemas.user_settings import ServerRailLayout


async def get_server_rail_layout(user: UserPublic) -> ServerRailLayout:
    if database.is_connected:
        return await user_settings_repository.get_server_rail_layout(user.id)
    return demo_store.get_server_rail_layout(user.id)


async def set_server_rail_layout(
    *,
    user: UserPublic,
    layout: ServerRailLayout,
) -> ServerRailLayout:
    if database.is_connected:
        return await user_settings_repository.set_server_rail_layout(user_id=user.id, layout=layout)
    return demo_store.set_server_rail_layout(user.id, layout)
