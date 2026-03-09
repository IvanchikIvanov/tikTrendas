from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from trend2video.apps.api.deps import get_search_job_repository
from trend2video.apps.worker.jobs.build_content_candidates import run_build_content_candidates
from trend2video.apps.worker.jobs.collect_keyword_trends import run_collect_keyword_trends
from trend2video.apps.worker.jobs.collect_related_videos import run_collect_related_videos
from trend2video.apps.worker.jobs.generate_scripts import run_generate_scripts
from trend2video.domain.entities.search_job import SearchJobMode, TrendSearchJob
from trend2video.persistence.repositories.search_job_repository import SearchJobRepository


router = APIRouter(prefix="/search-jobs", tags=["search_jobs"])


class SearchJobPatch(BaseModel):
    name: str | None = None
    countries: list[str] | None = None
    time_window: str | None = None
    top_keywords_limit: int | None = None
    related_videos_per_keyword: int | None = None
    source_types: list[str] | None = None
    min_popularity_change: float | None = None
    language: str | None = None
    product_tags: list[str] | None = None
    mode: SearchJobMode | None = None
    is_active: bool | None = None


@router.post("")
async def create_search_job(
    payload: TrendSearchJob,
    repo: SearchJobRepository = Depends(get_search_job_repository),
) -> dict[str, Any]:
    job = await repo.create(payload)
    return job.model_dump(mode="json")


@router.get("")
async def list_search_jobs(
    repo: SearchJobRepository = Depends(get_search_job_repository),
) -> list[dict[str, Any]]:
    return [job.model_dump(mode="json") for job in await repo.list()]


@router.get("/{job_id}")
async def get_search_job(
    job_id: int,
    repo: SearchJobRepository = Depends(get_search_job_repository),
) -> dict[str, Any]:
    job = await repo.get_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="search job not found")
    return job.model_dump(mode="json")


@router.patch("/{job_id}")
async def patch_search_job(
    job_id: int,
    payload: SearchJobPatch,
    repo: SearchJobRepository = Depends(get_search_job_repository),
) -> dict[str, Any]:
    job = await repo.update(job_id, payload.model_dump(exclude_unset=True))
    if job is None:
        raise HTTPException(status_code=404, detail="search job not found")
    return job.model_dump(mode="json")


@router.post("/{job_id}/run-keywords")
async def run_keywords(job_id: int) -> dict[str, int]:
    return await run_collect_keyword_trends(job_id=job_id)


@router.post("/{job_id}/run-related-videos")
async def run_related_videos(job_id: int) -> dict[str, int]:
    return await run_collect_related_videos(job_id=job_id)


@router.post("/{job_id}/build-candidates")
async def build_candidates(job_id: int) -> dict[str, int]:
    return await run_build_content_candidates(job_id=job_id)


@router.post("/{job_id}/generate-scripts")
async def generate_scripts(job_id: int) -> dict[str, int]:
    return await run_generate_scripts(job_id=job_id)
