from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ContentCandidateStatus(str, Enum):
    CANDIDATE = "candidate"
    SCRIPT_GENERATED = "script_generated"
    REJECTED = "rejected"


class ContentCandidate(BaseModel):
    id: int | None = None
    job_id: int
    keyword_trend_id: int
    candidate_type: str
    product_relevance_score: float
    signal_score: float
    scriptability_score: float
    recommended_angle: str | None = None
    status: ContentCandidateStatus = ContentCandidateStatus.CANDIDATE
    metadata_json: dict = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
