from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.manual_trend import ManualTrendInput
from trend2video.domain.entities.manual_trend_reference import ManualTrendReference
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.persistence.models.manual_trend import ManualTrendInputORM
from trend2video.persistence.models.manual_trend_reference import ManualTrendReferenceORM


class ManualTrendRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: ManualTrendInputORM) -> ManualTrendInput:
        return ManualTrendInput(
            id=orm.id,
            title=orm.title,
            trend_type=orm.trend_type,
            country=orm.country,
            time_window=orm.time_window,
            notes=orm.notes,
            reference_hook_texts=orm.reference_hook_texts_json or [],
            related_video_urls=orm.related_video_urls_json or [],
            manual_tags=orm.manual_tags_json or [],
            priority=orm.priority,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def _reference_to_entity(self, orm: ManualTrendReferenceORM) -> ManualTrendReference:
        return ManualTrendReference(
            id=orm.id,
            manual_trend_input_id=orm.manual_trend_input_id,
            source_platform=orm.source_platform,
            source_url=orm.source_url,
            hook_text=orm.hook_text,
            notes=orm.notes,
            metadata_json=orm.metadata_json or {},
            created_at=orm.created_at,
        )

    async def create(
        self,
        trend: ManualTrendInput,
        references: list[ManualTrendReference] | None = None,
    ) -> ManualTrendInput:
        orm = ManualTrendInputORM(
            title=trend.title,
            trend_type=trend.trend_type,
            country=trend.country,
            time_window=trend.time_window,
            notes=trend.notes,
            reference_hook_texts_json=trend.reference_hook_texts,
            related_video_urls_json=trend.related_video_urls,
            manual_tags_json=trend.manual_tags,
            priority=trend.priority,
            status=trend.status.value if hasattr(trend.status, "value") else str(trend.status),
        )
        self._session.add(orm)
        await self._session.flush()
        for reference in references or []:
            self._session.add(
                ManualTrendReferenceORM(
                    manual_trend_input_id=orm.id,
                    source_platform=reference.source_platform,
                    source_url=reference.source_url,
                    hook_text=reference.hook_text,
                    notes=reference.notes,
                    metadata_json=reference.metadata_json,
                )
            )
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def list_all(self) -> Sequence[ManualTrendInput]:
        stmt: Select[tuple[ManualTrendInputORM]] = select(ManualTrendInputORM).order_by(
            ManualTrendInputORM.priority.asc(),
            ManualTrendInputORM.created_at.desc(),
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_by_id(self, trend_id: int) -> ManualTrendInput | None:
        orm = await self._session.get(ManualTrendInputORM, trend_id)
        return None if orm is None else self._to_entity(orm)

    async def update(self, trend_id: int, **changes: object) -> ManualTrendInput | None:
        orm = await self._session.get(ManualTrendInputORM, trend_id)
        if orm is None:
            return None
        for field, value in changes.items():
            if field == "reference_hook_texts":
                orm.reference_hook_texts_json = list(value) if value is not None else []
            elif field == "related_video_urls":
                orm.related_video_urls_json = list(value) if value is not None else []
            elif field == "manual_tags":
                orm.manual_tags_json = list(value) if value is not None else []
            elif field == "status" and value is not None:
                orm.status = value.value if hasattr(value, "value") else str(value)
            elif hasattr(orm, field):
                setattr(orm, field, value)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def list_references(self, trend_id: int) -> Sequence[ManualTrendReference]:
        stmt: Select[tuple[ManualTrendReferenceORM]] = (
            select(ManualTrendReferenceORM)
            .where(ManualTrendReferenceORM.manual_trend_input_id == trend_id)
            .order_by(ManualTrendReferenceORM.created_at.asc())
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._reference_to_entity(row) for row in rows]

    def as_related_videos(self, trend: ManualTrendInput) -> list[RelatedVideo]:
        return [
            RelatedVideo(
                keyword_trend_id=trend.id or 0,
                source_platform="manual",
                source_url=url,
                overlay_text=trend.reference_hook_texts[idx] if idx < len(trend.reference_hook_texts) else None,
                transcript=trend.notes,
                topic_tags_json=trend.manual_tags,
                visual_tags_json=[],
                metadata_json={"manual_trend_input_id": trend.id, "source": "manual"},
            )
            for idx, url in enumerate(trend.related_video_urls)
        ]
