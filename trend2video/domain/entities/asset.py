from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Asset(BaseModel):
    id: int | None = None
    asset_type: str
    asset_tag: str
    path: str
    duration_sec: float | None = None
    metadata_json: dict = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
