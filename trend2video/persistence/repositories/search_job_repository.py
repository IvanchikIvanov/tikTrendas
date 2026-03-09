from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.search_job import TrendSearchJob
from trend2video.persistence.models.search_job import TrendSearchJobORM


class SearchJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: TrendSearchJobORM) -> TrendSearchJob:
        return TrendSearchJob(
            id=orm.id,
            name=orm.name,
            countries=list(orm.countries_json or []),
            time_window=orm.time_window,
            top_keywords_limit=orm.top_keywords_limit,
            related_videos_per_keyword=orm.related_videos_per_keyword,
            source_types=list(orm.source_types_json or []),
            min_popularity_change=orm.min_popularity_change,
            language=orm.language,
            product_tags=list(orm.product_tags_json or []),
            mode=orm.mode,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def create(self, job: TrendSearchJob) -> TrendSearchJob:
        orm = TrendSearchJobORM(
            name=job.name,
            countries_json=job.countries,
            time_window=job.time_window,
            top_keywords_limit=job.top_keywords_limit,
            related_videos_per_keyword=job.related_videos_per_keyword,
            source_types_json=job.source_types,
            min_popularity_change=job.min_popularity_change,
            language=job.language,
            product_tags_json=job.product_tags,
            mode=job.mode.value,
            is_active=job.is_active,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def list(self) -> Sequence[TrendSearchJob]:
        stmt: Select[tuple[TrendSearchJobORM]] = select(TrendSearchJobORM).order_by(TrendSearchJobORM.created_at.desc())
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_by_id(self, job_id: int) -> TrendSearchJob | None:
        orm = await self._session.get(TrendSearchJobORM, job_id)
        return None if orm is None else self._to_entity(orm)

    async def update(self, job_id: int, patch: dict) -> TrendSearchJob | None:
        orm = await self._session.get(TrendSearchJobORM, job_id)
        if orm is None:
            return None
        field_map = {
            "countries": "countries_json",
            "source_types": "source_types_json",
            "product_tags": "product_tags_json",
        }
        for key, value in patch.items():
            if value is None:
                continue
            if key == "mode" and hasattr(value, "value"):
                value = value.value
            setattr(orm, field_map.get(key, key), value)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def list_active(self) -> Sequence[TrendSearchJob]:
        stmt: Select[tuple[TrendSearchJobORM]] = select(TrendSearchJobORM).where(TrendSearchJobORM.is_active.is_(True))
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]
