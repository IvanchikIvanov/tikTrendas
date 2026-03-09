from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class RelatedVideo(BaseModel):
    id: int | None = None
    keyword_trend_id: int
    source_platform: str
    source_url: str
    creator_name: str | None = None
    thumbnail_url: str | None = None
    storage_path: str | None = None
    overlay_text: str | None = None
    transcript: str | None = None
    duration_sec: float | None = None
    visual_tags_json: list[str] = Field(default_factory=list)
    topic_tags_json: list[str] = Field(default_factory=list)
    metadata_json: dict = Field(default_factory=dict)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
