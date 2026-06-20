from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.permissions import MAX_JS_SAFE_INTEGER


class ServerRailGuildItem(BaseModel):
    type: Literal["guild"]
    guild_id: int = Field(ge=1, le=MAX_JS_SAFE_INTEGER)


class ServerRailFolderItem(BaseModel):
    type: Literal["folder"]
    folder_id: str = Field(min_length=1, max_length=64)


ServerRailItem = ServerRailGuildItem | ServerRailFolderItem


class ServerRailFolder(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=40)
    color: str | None = Field(default=None, max_length=32)
    collapsed: bool = False
    guild_ids: list[int] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def validate_unique_guilds(self) -> ServerRailFolder:
        if len(set(self.guild_ids)) != len(self.guild_ids):
            raise ValueError("folder guild_ids must be unique")
        return self


class ServerRailLayout(BaseModel):
    items: list[ServerRailItem] = Field(default_factory=list, max_length=200)
    folders: list[ServerRailFolder] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def validate_layout_uniqueness(self) -> ServerRailLayout:
        folder_ids = [folder.id for folder in self.folders]
        if len(set(folder_ids)) != len(folder_ids):
            raise ValueError("folder ids must be unique")

        item_folder_ids = [
            item.folder_id
            for item in self.items
            if isinstance(item, ServerRailFolderItem)
        ]
        missing_folders = set(item_folder_ids) - set(folder_ids)
        if missing_folders:
            raise ValueError("layout item references unknown folder")

        guild_ids: list[int] = []
        for item in self.items:
            if isinstance(item, ServerRailGuildItem):
                guild_ids.append(item.guild_id)
        for folder in self.folders:
            guild_ids.extend(folder.guild_ids)
        if len(set(guild_ids)) != len(guild_ids):
            raise ValueError("guild ids must appear at most once in the rail layout")
        return self
