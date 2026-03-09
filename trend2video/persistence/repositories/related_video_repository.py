from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.persistence.models.keyword_trend import KeywordTrendORM
from trend2video.persistence.models.related_video import RelatedVideoORM


class RelatedVideoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: RelatedVideoORM) -> RelatedVideo:
        return RelatedVideo(
            id=orm.id,
            keyword_trend_id=orm.keyword_trend_id,
            source_platform=orm.source_platform,
            source_url=orm.source_url,
            creator_name=orm.creator_name,
            thumbnail_url=orm.thumbnail_url,
            storage_path=orm.storage_path,
            overlay_text=orm.overlay_text,
            transcript=orm.transcript,
            duration_sec=orm.duration_sec,
            visual_tags_json=list(orm.visual_tags_json or []),
            topic_tags_json=list(orm.topic_tags_json or []),
            metadata_json=orm.metadata_json or {},
            collected_at=orm.collected_at,
        )

    async def bulk_insert(self, videos: list[RelatedVideo]) -> list[RelatedVideo]:
        persisted: list[RelatedVideo] = []
        for video in videos:
            stmt: Select[tuple[RelatedVideoORM]] = select(RelatedVideoORM).where(
                RelatedVideoORM.keyword_trend_id == video.keyword_trend_id,
                RelatedVideoORM.source_url == video.source_url,
            )
            existing = (await self._session.execute(stmt)).scalars().first()
            if existing is None:
                existing = RelatedVideoORM(
                    keyword_trend_id=video.keyword_trend_id,
                    source_platform=video.source_platform,
                    source_url=video.source_url,
                )
                self._session.add(existing)
            existing.creator_name = video.creator_name
            existing.thumbnail_url = video.thumbnail_url
            existing.storage_path = video.storage_path
            existing.overlay_text = video.overlay_text
            existing.transcript = video.transcript
            existing.duration_sec = video.duration_sec
            existing.visual_tags_json = video.visual_tags_json
            existing.topic_tags_json = video.topic_tags_json
            existing.metadata_json = video.metadata_json
            existing.collected_at = video.collected_at
            await self._session.flush()
            persisted.append(self._to_entity(existing))
        await self._session.commit()
        return persisted

    async def list_for_keyword_trend(self, keyword_trend_id: int) -> Sequence[RelatedVideo]:
        stmt: Select[tuple[RelatedVideoORM]] = select(RelatedVideoORM).where(RelatedVideoORM.keyword_trend_id == keyword_trend_id)
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]

    async def exists_for_keyword_trend(self, keyword_trend_id: int) -> bool:
        stmt: Select[tuple[int]] = select(RelatedVideoORM.id).where(RelatedVideoORM.keyword_trend_id == keyword_trend_id).limit(1)
        return (await self._session.execute(stmt)).first() is not None

    async def list_for_job(self, job_id: int) -> Sequence[RelatedVideo]:
        stmt: Select[tuple[RelatedVideoORM]] = (
            select(RelatedVideoORM)
            .join(KeywordTrendORM, KeywordTrendORM.id == RelatedVideoORM.keyword_trend_id)
            .where(KeywordTrendORM.job_id == job_id)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]
