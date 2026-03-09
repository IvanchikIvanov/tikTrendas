from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.publish_job import PublishJob
from trend2video.persistence.models.publish_job import PublishJobORM


class PublishJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: PublishJobORM) -> PublishJob:
        return PublishJob(
            id=orm.id,
            render_job_id=orm.render_job_id,
            target_platform=orm.target_platform,
            status=orm.status,
            payload_json=orm.payload_json or {},
            result_json=orm.result_json or {},
            scheduled_at=orm.scheduled_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def create(self, job: PublishJob) -> PublishJob:
        orm = PublishJobORM(
            render_job_id=job.render_job_id,
            target_platform=job.target_platform,
            status=job.status.value if hasattr(job.status, "value") else str(job.status),
            payload_json=job.payload_json,
            result_json=job.result_json,
            scheduled_at=job.scheduled_at,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def list_all(self) -> Sequence[PublishJob]:
        stmt: Select[tuple[PublishJobORM]] = select(PublishJobORM).order_by(PublishJobORM.created_at.desc())
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]
