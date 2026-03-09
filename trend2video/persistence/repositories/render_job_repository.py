from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.render_job import RenderJob, RenderJobStatus
from trend2video.persistence.models.render_job import RenderJobORM


class RenderJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: RenderJobORM) -> RenderJob:
        return RenderJob(
            id=orm.id,
            content_candidate_id=orm.content_candidate_id,
            script_id=orm.script_id,
            template_id=orm.template_id,
            status=orm.status,
            render_manifest_json=orm.render_manifest_json or {},
            output_path=orm.output_path,
            preview_path=orm.preview_path,
            error=orm.error,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def create(self, job: RenderJob) -> RenderJob:
        orm = RenderJobORM(
            content_candidate_id=job.content_candidate_id,
            script_id=job.script_id,
            template_id=job.template_id,
            status=job.status.value if hasattr(job.status, "value") else str(job.status),
            render_manifest_json=job.render_manifest_json,
            output_path=job.output_path,
            preview_path=job.preview_path,
            error=job.error,
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def update_result(
        self,
        render_job_id: int,
        *,
        status: RenderJobStatus | str,
        manifest: dict | None = None,
        output_path: str | None = None,
        preview_path: str | None = None,
        error: str | None = None,
    ) -> RenderJob | None:
        orm = await self._session.get(RenderJobORM, render_job_id)
        if orm is None:
            return None
        orm.status = status.value if hasattr(status, "value") else str(status)
        if manifest is not None:
            orm.render_manifest_json = manifest
        if output_path is not None:
            orm.output_path = output_path
        if preview_path is not None:
            orm.preview_path = preview_path
        orm.error = error
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def get_by_id(self, render_job_id: int) -> RenderJob | None:
        orm = await self._session.get(RenderJobORM, render_job_id)
        return None if orm is None else self._to_entity(orm)

    async def list_all(self) -> Sequence[RenderJob]:
        stmt: Select[tuple[RenderJobORM]] = select(RenderJobORM).order_by(RenderJobORM.created_at.desc())
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]
