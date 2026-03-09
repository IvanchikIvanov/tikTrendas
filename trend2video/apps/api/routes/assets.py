from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from trend2video.apps.api.deps import get_asset_repository
from trend2video.domain.entities.asset import Asset
from trend2video.persistence.repositories.asset_repository import AssetRepository


router = APIRouter(prefix="/assets", tags=["assets"])


class AssetCreatePayload(BaseModel):
    asset_type: str
    asset_tag: str
    path: str
    duration_sec: float | None = None
    metadata_json: dict = Field(default_factory=dict)
    is_active: bool = True


@router.post("")
async def create_asset(
    payload: AssetCreatePayload,
    repo: AssetRepository = Depends(get_asset_repository),
) -> dict[str, Any]:
    asset = await repo.create(Asset(**payload.model_dump()))
    return asset.model_dump(mode="json")


@router.get("")
async def list_assets(
    repo: AssetRepository = Depends(get_asset_repository),
) -> list[dict[str, Any]]:
    return [asset.model_dump(mode="json") for asset in await repo.list_active()]
