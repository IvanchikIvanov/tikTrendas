from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.script import GeneratedScript
from trend2video.persistence.models.script import ScriptORM
from trend2video.persistence.models.template import TemplateORM
from trend2video.persistence.models.trend import TrendORM


class ScriptRepository:
    """Работа с таблицей scripts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_script(
        self,
        trend: TrendORM,
        template: TemplateORM,
        script: GeneratedScript,
    ) -> ScriptORM:
        obj = ScriptORM(
            trend_id=trend.id,
            template_id=template.id,
            script_json=script.model_dump(mode="json"),
        )
        self._session.add(obj)
        await self._session.commit()
        await self._session.refresh(obj)
        return obj

    async def get_by_trend_id(self, trend_id: int) -> ScriptORM | None:
        stmt: Select[tuple[ScriptORM]] = select(ScriptORM).where(ScriptORM.trend_id == trend_id)
        row = (await self._session.execute(stmt)).scalars().first()
        return row

    async def exists_for_trend(self, trend_id: int) -> bool:
        return (await self.get_by_trend_id(trend_id)) is not None

    async def list_scripts(self, limit: int = 50, offset: int = 0) -> Sequence[ScriptORM]:
        stmt: Select[tuple[ScriptORM]] = (
            select(ScriptORM).order_by(ScriptORM.created_at.desc()).offset(offset).limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

