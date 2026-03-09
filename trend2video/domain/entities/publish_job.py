from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PublishJobStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"


class PublishJob(BaseModel):
    id: int | None = None
    render_job_id: int
    target_platform: str
    status: PublishJobStatus = PublishJobStatus.PENDING
    payload_json: dict = Field(default_factory=dict)
    result_json: dict = Field(default_factory=dict)
    scheduled_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
