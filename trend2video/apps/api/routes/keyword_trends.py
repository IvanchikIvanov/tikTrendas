from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from trend2video.apps.api.deps import get_keyword_trend_repository
from trend2video.persistence.repositories.keyword_trend_repository import KeywordTrendRepository


router = APIRouter(prefix="/keyword-trends", tags=["keyword_trends"])


@router.get("")
async def list_keyword_trends(
    job_id: int = Query(..., ge=1),
    country: str | None = Query(None),
    time_window: str | None = Query(None),
    min_popularity_change: float | None = Query(None),
    repo: KeywordTrendRepository = Depends(get_keyword_trend_repository),
) -> list[dict[str, Any]]:
    items = list(await repo.list_for_job(job_id))
    if country is not None:
        items = [item for item in items if item.country == country]
    if time_window is not None:
        items = [item for item in items if item.time_window == time_window]
    if min_popularity_change is not None:
        items = [item for item in items if (item.popularity_change or 0.0) >= min_popularity_change]
    return [item.model_dump(mode="json") for item in items]
