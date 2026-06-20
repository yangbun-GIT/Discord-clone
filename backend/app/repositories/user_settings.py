from __future__ import annotations

import json
from typing import Any

from app.db.pool import database
from app.schemas.user_settings import ServerRailLayout


class UserSettingsRepository:
    async def get_server_rail_layout(self, user_id: int) -> ServerRailLayout:
        row = await database.fetchrow(
            """
            SELECT layout_json
            FROM user_server_rail_layouts
            WHERE user_id = $1
            """,
            user_id,
        )
        if row is None:
            return ServerRailLayout()
        raw_layout = row["layout_json"]
        layout_data: Any = json.loads(raw_layout) if isinstance(raw_layout, str) else raw_layout
        return ServerRailLayout.model_validate(layout_data)

    async def set_server_rail_layout(
        self,
        *,
        user_id: int,
        layout: ServerRailLayout,
    ) -> ServerRailLayout:
        layout_json = layout.model_dump(mode="json")
        await database.execute(
            """
            INSERT INTO user_server_rail_layouts (user_id, layout_json, updated_at)
            VALUES ($1, $2::jsonb, now())
            ON CONFLICT (user_id)
            DO UPDATE SET layout_json = EXCLUDED.layout_json, updated_at = now()
            """,
            user_id,
            json.dumps(layout_json, separators=(",", ":")),
        )
        return layout


user_settings_repository = UserSettingsRepository()
