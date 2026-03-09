from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class SearchJobMode(str, Enum):
    NEW_AND_GROWING = "new_and_growing"
    NEW_ONLY = "new_only"
    GROWING_ONLY = "growing_only"


class TrendSearchJob(BaseModel):
    id: int | None = None
    name: str
    countries: list[str] = Field(default_factory=list, min_length=1)
    time_window: str = "7d"
    top_keywords_limit: int = Field(default=10, ge=1, le=100)
    related_videos_per_keyword: int = Field(default=3, ge=0, le=20)
    source_types: list[str] = Field(default_factory=lambda: ["static"])
    min_popularity_change: float = 0.0
    language: str | None = None
    product_tags: list[str] = Field(default_factory=list)
    mode: SearchJobMode = SearchJobMode.NEW_AND_GROWING
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("countries", "source_types", "product_tags")
    @classmethod
    def strip_values(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value and value.strip()]

    @field_validator("time_window")
    @classmethod
    def validate_time_window(cls, value: str) -> str:
        allowed = {"1d", "7d", "30d", "90d"}
        if value not in allowed:
            raise ValueError(f"time_window must be one of {sorted(allowed)}")
        return value
