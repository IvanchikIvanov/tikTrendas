from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from trend2video.apps.api.deps import get_related_video_repository
from trend2video.persistence.repositories.related_video_repository import RelatedVideoRepository


router = APIRouter(prefix="/related-videos", tags=["related_videos"])


@router.get("")
async def list_related_videos(
    keyword_trend_id: int | None = Query(None, ge=1),
    job_id: int | None = Query(None, ge=1),
    repo: RelatedVideoRepository = Depends(get_related_video_repository),
) -> list[dict[str, Any]]:
    if keyword_trend_id is not None:
        items = await repo.list_for_keyword_trend(keyword_trend_id)
    elif job_id is not None:
        items = await repo.list_for_job(job_id)
    else:
        items = []
    return [item.model_dump(mode="json") for item in items]
