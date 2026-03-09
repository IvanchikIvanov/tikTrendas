from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.trend import NormalizedTrend, TrendStatus
from trend2video.persistence.models.trend import TrendORM


class TrendRepository:
    """Работа с таблицей trends."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_trends(
        self,
        trends: list[NormalizedTrend],
    ) -> tuple[list[TrendORM], dict[str, int]]:
        inserted = 0
        updated = 0
        result: list[TrendORM] = []

        for trend in trends:
            existing = await self._get_by_source_external_id(trend.source, trend.external_id)
            if existing is None:
                obj = TrendORM(
                    source=trend.source,
                    external_id=trend.external_id,
                    trend_type=trend.trend_type,
                    title=trend.title,
                    region=trend.region,
                    industry=trend.industry,
                    rank=trend.rank,
                    heat=trend.heat,
                    velocity=trend.velocity,
                    tags_json=trend.tags,
                    raw_payload_json=trend.raw_payload,
                    score=None,
                    status=TrendStatus.DISCOVERED,
                    discovered_at=trend.discovered_at,
                )
                self._session.add(obj)
                result.append(obj)
                inserted += 1
            else:
                existing.rank = trend.rank
                existing.heat = trend.heat
                existing.velocity = trend.velocity
                existing.tags_json = trend.tags
                existing.raw_payload_json = trend.raw_payload
                result.append(existing)
                updated += 1

        await self._session.commit()
        summary = {"inserted_count": inserted, "updated_count": updated, "skipped_count": 0}
        return result, summary

    async def get_unprocessed_trends(self, limit: int = 20) -> list[TrendORM]:
        stmt: Select[tuple[TrendORM]] = (
            select(TrendORM)
            .where(TrendORM.status.in_([TrendStatus.DISCOVERED, TrendStatus.SCORED]))
            .order_by(TrendORM.discovered_at.desc())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

    async def update_score(self, trend_id: int, score: float) -> None:
        stmt = (
            update(TrendORM)
            .where(TrendORM.id == trend_id)
            .values(score=score, status=TrendStatus.SCORED)
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def mark_status(self, trend_id: int, status: TrendStatus) -> None:
        stmt = update(TrendORM).where(TrendORM.id == trend_id).values(status=status)
        await self._session.execute(stmt)
        await self._session.commit()

    async def list_trends(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[TrendORM]:
        stmt: Select[tuple[TrendORM]] = select(TrendORM)
        if status is not None:
            stmt = stmt.where(TrendORM.status == status)
        stmt = stmt.order_by(TrendORM.discovered_at.desc()).offset(offset).limit(limit)
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

    async def get_by_source_external_id(self, source: str, external_id: str) -> TrendORM | None:
        return await self._get_by_source_external_id(source, external_id)

    async def _get_by_source_external_id(self, source: str, external_id: str) -> TrendORM | None:
        stmt: Select[tuple[TrendORM]] = select(TrendORM).where(
            TrendORM.source == source,
            TrendORM.external_id == external_id,
        )
        row = (await self._session.execute(stmt)).scalars().first()
        return row

