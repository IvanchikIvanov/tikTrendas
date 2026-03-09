from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ManualTrendReference(BaseModel):
    id: int | None = None
    manual_trend_input_id: int
    source_platform: str
    source_url: str
    hook_text: str | None = None
    notes: str | None = None
    metadata_json: dict = Field(default_factory=dict)
    created_at: datetime | None = None
