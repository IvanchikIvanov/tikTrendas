from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from trend2video.apps.api.deps import get_publish_job_repository, get_render_job_repository
from trend2video.domain.entities.publish_job import PublishJob
from trend2video.persistence.repositories.publish_job_repository import PublishJobRepository
from trend2video.persistence.repositories.render_job_repository import RenderJobRepository


router = APIRouter(tags=["publish-jobs"])


class PublishJobCreatePayload(BaseModel):
    target_platform: str
    payload_json: dict = Field(default_factory=dict)
    scheduled_at: str | None = None


@router.post("/renders/{render_job_id}/publish-jobs")
async def create_publish_job(
    render_job_id: int,
    payload: PublishJobCreatePayload,
    render_repo: RenderJobRepository = Depends(get_render_job_repository),
    publish_repo: PublishJobRepository = Depends(get_publish_job_repository),
) -> dict[str, Any]:
    render_job = await render_repo.get_by_id(render_job_id)
    if render_job is None:
        raise HTTPException(status_code=404, detail="render not found")
    job = await publish_repo.create(
        PublishJob(
            render_job_id=render_job_id,
            target_platform=payload.target_platform,
            payload_json=payload.payload_json,
        )
    )
    return job.model_dump(mode="json")


@router.get("/publish-jobs")
async def list_publish_jobs(
    repo: PublishJobRepository = Depends(get_publish_job_repository),
) -> list[dict[str, Any]]:
    return [job.model_dump(mode="json") for job in await repo.list_all()]
