from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from trend2video.apps.api.deps import get_content_candidate_repository, get_manual_trend_repository
from trend2video.apps.worker.jobs.build_manual_candidates import run_build_manual_candidates
from trend2video.domain.entities.manual_trend import ManualTrendInput
from trend2video.domain.entities.manual_trend_reference import ManualTrendReference
from trend2video.persistence.repositories.content_candidate_repository import ContentCandidateRepository
from trend2video.persistence.repositories.manual_trend_repository import ManualTrendRepository


router = APIRouter(prefix="/manual-trends", tags=["manual-trends"])


class ManualTrendReferencePayload(BaseModel):
    source_platform: str
    source_url: str
    hook_text: str | None = None
    notes: str | None = None
    metadata_json: dict = Field(default_factory=dict)


class ManualTrendCreatePayload(BaseModel):
    title: str
    trend_type: str
    country: str
    time_window: str
    notes: str | None = None
    reference_hook_texts: list[str] = Field(default_factory=list)
    related_video_urls: list[str] = Field(default_factory=list)
    manual_tags: list[str] = Field(default_factory=list)
    priority: int = 1
    status: str = "new"
    references: list[ManualTrendReferencePayload] = Field(default_factory=list)


class ManualTrendPatchPayload(BaseModel):
    title: str | None = None
    trend_type: str | None = None
    country: str | None = None
    time_window: str | None = None
    notes: str | None = None
    reference_hook_texts: list[str] | None = None
    related_video_urls: list[str] | None = None
    manual_tags: list[str] | None = None
    priority: int | None = None
    status: str | None = None


@router.post("")
async def create_manual_trend(
    payload: ManualTrendCreatePayload,
    repo: ManualTrendRepository = Depends(get_manual_trend_repository),
) -> dict[str, Any]:
    trend = ManualTrendInput(**payload.model_dump(exclude={"references"}))
    references = [
        ManualTrendReference(manual_trend_input_id=0, **reference.model_dump())
        for reference in payload.references
    ]
    created = await repo.create(trend, references)
    return created.model_dump(mode="json")


@router.get("")
async def list_manual_trends(
    repo: ManualTrendRepository = Depends(get_manual_trend_repository),
) -> list[dict[str, Any]]:
    return [trend.model_dump(mode="json") for trend in await repo.list_all()]


@router.get("/{trend_id}")
async def get_manual_trend(
    trend_id: int,
    repo: ManualTrendRepository = Depends(get_manual_trend_repository),
    candidate_repo: ContentCandidateRepository = Depends(get_content_candidate_repository),
) -> dict[str, Any]:
    trend = await repo.get_by_id(trend_id)
    if trend is None:
        raise HTTPException(status_code=404, detail="manual trend not found")
    return {
        **trend.model_dump(mode="json"),
        "references": [reference.model_dump(mode="json") for reference in await repo.list_references(trend_id)],
        "candidates": [candidate.model_dump(mode="json") for candidate in await candidate_repo.list_for_manual_trend(trend_id)],
    }


@router.patch("/{trend_id}")
async def patch_manual_trend(
    trend_id: int,
    payload: ManualTrendPatchPayload,
    repo: ManualTrendRepository = Depends(get_manual_trend_repository),
) -> dict[str, Any]:
    updated = await repo.update(trend_id, **payload.model_dump(exclude_none=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="manual trend not found")
    return updated.model_dump(mode="json")


@router.post("/{trend_id}/build-candidate")
async def build_candidate_for_manual_trend(
    trend_id: int,
    repo: ManualTrendRepository = Depends(get_manual_trend_repository),
) -> dict[str, int]:
    trend = await repo.get_by_id(trend_id)
    if trend is None:
        raise HTTPException(status_code=404, detail="manual trend not found")
    return await run_build_manual_candidates(trend_id)
