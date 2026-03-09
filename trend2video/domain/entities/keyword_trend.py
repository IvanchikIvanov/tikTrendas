from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class KeywordTrend(BaseModel):
    id: int | None = None
    job_id: int
    source: str
    country: str
    time_window: str
    keyword: str
    rank: int | None = None
    popularity: float | None = None
    popularity_change: float | None = None
    ctr: float | None = None
    keyword_type: str | None = None
    industry: str | None = None
    objective: str | None = None
    details_url: str | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload_json: dict = Field(default_factory=dict)
