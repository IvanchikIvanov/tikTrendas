from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.persistence.models.keyword_trend import KeywordTrendORM
from trend2video.persistence.models.related_video import RelatedVideoORM


class KeywordTrendRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: KeywordTrendORM) -> KeywordTrend:
        return KeywordTrend(
            id=orm.id,
            job_id=orm.job_id,
            source=orm.source,
            country=orm.country,
            time_window=orm.time_window,
            keyword=orm.keyword,
            rank=orm.rank,
            popularity=orm.popularity,
            popularity_change=orm.popularity_change,
            ctr=orm.ctr,
            keyword_type=orm.keyword_type,
            industry=orm.industry,
            objective=orm.objective,
            details_url=orm.details_url,
            raw_payload_json=orm.raw_payload_json or {},
            first_seen_at=orm.first_seen_at,
            last_seen_at=orm.last_seen_at,
            collected_at=orm.collected_at,
        )

    async def bulk_upsert(self, items: list[KeywordTrend]) -> list[KeywordTrend]:
        persisted: list[KeywordTrend] = []
        for item in items:
            stmt: Select[tuple[KeywordTrendORM]] = select(KeywordTrendORM).where(
                KeywordTrendORM.job_id == item.job_id,
                KeywordTrendORM.country == item.country,
                KeywordTrendORM.time_window == item.time_window,
                KeywordTrendORM.keyword == item.keyword,
            )
            existing = (await self._session.execute(stmt)).scalars().first()
            if existing is None:
                existing = KeywordTrendORM(
                    job_id=item.job_id,
                    source=item.source,
                    country=item.country,
                    time_window=item.time_window,
                    keyword=item.keyword,
                )
                self._session.add(existing)
            existing.rank = item.rank
            existing.popularity = item.popularity
            existing.popularity_change = item.popularity_change
            existing.ctr = item.ctr
            existing.keyword_type = item.keyword_type
            existing.industry = item.industry
            existing.objective = item.objective
            existing.details_url = item.details_url
            existing.raw_payload_json = item.raw_payload_json
            existing.first_seen_at = existing.first_seen_at or item.first_seen_at or item.collected_at
            existing.last_seen_at = item.last_seen_at or item.collected_at
            existing.collected_at = item.collected_at
            await self._session.flush()
            persisted.append(self._to_entity(existing))
        await self._session.commit()
        return persisted

    async def list_for_job(self, job_id: int) -> Sequence[KeywordTrend]:
        stmt: Select[tuple[KeywordTrendORM]] = (
            select(KeywordTrendORM)
            .where(KeywordTrendORM.job_id == job_id)
            .order_by(KeywordTrendORM.popularity_change.desc().nullslast(), KeywordTrendORM.rank.asc().nullslast())
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]

    async def list_top_for_job(self, job_id: int, limit: int = 10) -> Sequence[KeywordTrend]:
        stmt: Select[tuple[KeywordTrendORM]] = (
            select(KeywordTrendORM)
            .where(KeywordTrendORM.job_id == job_id)
            .order_by(KeywordTrendORM.popularity_change.desc().nullslast(), KeywordTrendORM.rank.asc().nullslast())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_by_id(self, keyword_trend_id: int) -> KeywordTrend | None:
        orm = await self._session.get(KeywordTrendORM, keyword_trend_id)
        return None if orm is None else self._to_entity(orm)

    async def get_without_related_videos(self, job_id: int) -> Sequence[KeywordTrend]:
        stmt: Select[tuple[KeywordTrendORM]] = (
            select(KeywordTrendORM)
            .where(KeywordTrendORM.job_id == job_id)
            .where(~KeywordTrendORM.id.in_(select(RelatedVideoORM.keyword_trend_id)))
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]

    async def list_candidate_ready(self, job_id: int) -> Sequence[KeywordTrend]:
        stmt: Select[tuple[KeywordTrendORM]] = (
            select(KeywordTrendORM)
            .where(KeywordTrendORM.job_id == job_id)
            .where(KeywordTrendORM.id.in_(select(RelatedVideoORM.keyword_trend_id)))
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]
