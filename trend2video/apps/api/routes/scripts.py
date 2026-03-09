from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from trend2video.apps.api.deps import get_script_repository
from trend2video.persistence.repositories.script_repository import ScriptRepository


router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.get("")
async def list_scripts(
    script_repo: ScriptRepository = Depends(get_script_repository),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    scripts = await script_repo.list_all(limit=limit, offset=offset)
    return [
        {
            "id": script.id,
            "content_candidate_id": script.content_candidate_id,
            "keyword_trend_id": script.keyword_trend_id,
            "template_id": script.template_id,
            "status": script.status,
            "created_at": script.created_at,
        }
        for script in scripts
    ]
