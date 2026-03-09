from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.asset import Asset
from trend2video.persistence.models.asset import AssetORM


class AssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: AssetORM) -> Asset:
        return Asset(
            id=orm.id,
            asset_type=orm.asset_type,
            asset_tag=orm.asset_tag,
            path=orm.path,
            duration_sec=orm.duration_sec,
            metadata_json=orm.metadata_json or {},
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def create(self, asset: Asset) -> Asset:
        orm = AssetORM(
            asset_type=asset.asset_type,
            asset_tag=asset.asset_tag,
            path=asset.path,
            duration_sec=asset.duration_sec,
            metadata_json=asset.metadata_json,
            is_active=asset.is_active,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def list_active(self) -> Sequence[Asset]:
        stmt: Select[tuple[AssetORM]] = select(AssetORM).where(AssetORM.is_active.is_(True)).order_by(AssetORM.id.asc())
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]
