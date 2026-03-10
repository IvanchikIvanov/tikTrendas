from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from trend2video.apps.api.deps import get_content_candidate_repository
from trend2video.apps.worker.jobs.generate_scripts import run_generate_scripts
from trend2video.persistence.repositories.content_candidate_repository import ContentCandidateRepository


router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("")
async def list_candidates(
    job_id: int = Query(..., ge=1),
    repo: ContentCandidateRepository = Depends(get_content_candidate_repository),
) -> list[dict[str, Any]]:
    return [candidate.model_dump(mode="json") for candidate in await repo.list_for_job(job_id)]


@router.post("/{candidate_id}/generate-script")
async def generate_script_for_candidate(
    candidate_id: int,
    repo: ContentCandidateRepository = Depends(get_content_candidate_repository),
) -> dict[str, Any]:
    candidate = await repo.get_by_id(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="candidate not found")
    return await run_generate_scripts(candidate_id=candidate_id, limit=1)
