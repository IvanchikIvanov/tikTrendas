from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RenderJobStatus(str, Enum):
    PENDING = "pending"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class RenderJob(BaseModel):
    id: int | None = None
    content_candidate_id: int
    script_id: int
    template_id: str
    status: RenderJobStatus = RenderJobStatus.PENDING
    render_manifest_json: dict = Field(default_factory=dict)
    output_path: str | None = None
    preview_path: str | None = None
    error: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
