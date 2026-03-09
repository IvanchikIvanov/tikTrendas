from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ManualTrendStatus(str, Enum):
    NEW = "new"
    CANDIDATE_BUILT = "candidate_built"
    SCRIPT_GENERATED = "script_generated"
    RENDERED = "rendered"
    ARCHIVED = "archived"


class ManualTrendInput(BaseModel):
    id: int | None = None
    title: str
    trend_type: str
    country: str
    time_window: str
    notes: str | None = None
    reference_hook_texts: list[str] = Field(default_factory=list)
    related_video_urls: list[str] = Field(default_factory=list)
    manual_tags: list[str] = Field(default_factory=list)
    priority: int = 1
    status: ManualTrendStatus = ManualTrendStatus.NEW
    created_at: datetime | None = None
    updated_at: datetime | None = None
