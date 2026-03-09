from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TrendStatus(str, Enum):
    """Жизненный цикл тренда внутри системы."""

    DISCOVERED = "discovered"
    SCORED = "scored"
    TEMPLATE_SELECTED = "template_selected"
    SCRIPT_GENERATED = "script_generated"
    SKIPPED = "skipped"
    FAILED = "failed"


class NormalizedTrend(BaseModel):
    """Нормализованный тренд, независимый от конкретного источника."""

    source: str
    external_id: str
    trend_type: str
    title: str
    region: str
    industry: str | None = None
    rank: int | None = None
    heat: float | None = None
    velocity: float | None = None
    tags: list[str] = Field(default_factory=list)
    raw_payload: dict = Field(default_factory=dict)
    discovered_at: datetime
