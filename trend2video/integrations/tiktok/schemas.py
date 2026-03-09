from __future__ import annotations

from pydantic import BaseModel, Field


class KeywordInsightsRow(BaseModel):
    keyword: str
    country: str
    time_window: str
    rank: int | None = None
    popularity: float | None = None
    popularity_change: float | None = None
    ctr: float | None = None
    keyword_type: str | None = None
    industry: str | None = None
    objective: str | None = None
    details_url: str | None = None
    raw_payload_json: dict = Field(default_factory=dict)
    related_videos: list[dict] = Field(default_factory=list)
