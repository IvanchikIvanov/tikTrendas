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
    scripts = await script_repo.list_scripts(limit=limit, offset=offset)
    return [
        {
            "id": s.id,
            "trend_id": s.trend_id,
            "template_id": s.template_id,
            "status": s.status,
            "created_at": s.created_at,
        }
        for s in scripts
    ]

