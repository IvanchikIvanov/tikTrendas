from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from trend2video.apps.api.deps import get_render_job_repository, get_script_repository
from trend2video.apps.worker.jobs.render_drafts import run_render_draft
from trend2video.domain.entities.render_job import RenderJob
from trend2video.persistence.repositories.render_job_repository import RenderJobRepository
from trend2video.persistence.repositories.script_repository import ScriptRepository


router = APIRouter(prefix="/renders", tags=["renders"])


class RenderCreatePayload(BaseModel):
    script_id: int


@router.post("")
async def create_render(
    payload: RenderCreatePayload,
    script_repo: ScriptRepository = Depends(get_script_repository),
    render_repo: RenderJobRepository = Depends(get_render_job_repository),
) -> dict[str, Any]:
    script = await script_repo.get_by_id(payload.script_id)
    if script is None:
        raise HTTPException(status_code=404, detail="script not found")
    render_job = await render_repo.create(
        RenderJob(
            content_candidate_id=script.content_candidate_id,
            script_id=script.id,
            template_id=script.template_id,
        )
    )
    await run_render_draft(render_job.id)
    refreshed = await render_repo.get_by_id(render_job.id)
    return refreshed.model_dump(mode="json") if refreshed else render_job.model_dump(mode="json")


@router.get("")
async def list_renders(
    repo: RenderJobRepository = Depends(get_render_job_repository),
) -> list[dict[str, Any]]:
    return [job.model_dump(mode="json") for job in await repo.list_all()]


@router.get("/{render_job_id}")
async def get_render(
    render_job_id: int,
    repo: RenderJobRepository = Depends(get_render_job_repository),
) -> dict[str, Any]:
    render_job = await repo.get_by_id(render_job_id)
    if render_job is None:
        raise HTTPException(status_code=404, detail="render not found")
    return render_job.model_dump(mode="json")
