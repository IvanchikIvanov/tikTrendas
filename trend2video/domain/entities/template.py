from __future__ import annotations

from pydantic import BaseModel, Field, computed_field


class TemplateScene(BaseModel):
    """Описание одной сцены шаблона."""

    scene_id: str
    asset_type: str
    asset_tag: str
    duration_sec: float
    text_slot: str


class TemplateDefinition(BaseModel):
    """Полное описание шаблона для генерации видео."""

    template_key: str
    version: str

    name: str
    duration_sec: int
    aspect_ratio: str
    hooks: list[str]
    scene_plan: list[TemplateScene]
    caption_policy: dict = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    active: bool = True

    @computed_field  # type: ignore[misc]
    @property
    def id(self) -> str:
        """Собранный идентификатор вида key_version (для удобства)."""

        return f"{self.template_key}_{self.version}"

