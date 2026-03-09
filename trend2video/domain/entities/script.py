from __future__ import annotations

from pydantic import BaseModel, Field


class GeneratedScript(BaseModel):
    """Структурированный скрипт под выбранный шаблон."""

    content_candidate_id: str
    keyword_trend_id: str | None = None
    template_id: str
    hook_text: str
    pain_text: str | None = None
    solution_text: str | None = None
    outcome_text: str | None = None
    cta_text: str
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
