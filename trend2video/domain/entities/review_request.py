from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ReviewRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CHANGES = "needs_changes"


class ReviewRequest(BaseModel):
    id: int | None = None
    render_job_id: int
    channel_type: str
    status: ReviewRequestStatus = ReviewRequestStatus.PENDING
    reviewer: str | None = None
    review_comment: str | None = None
    created_at: datetime | None = None
    reviewed_at: datetime | None = None
