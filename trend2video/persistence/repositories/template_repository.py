from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.template import TemplateDefinition
from trend2video.persistence.models.template import TemplateORM


class TemplateRepository:
    """Работа с шаблонами в БД."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_templates(self) -> Sequence[TemplateORM]:
        stmt: Select[tuple[TemplateORM]] = select(TemplateORM).where(TemplateORM.is_active.is_(True))
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

    async def get_active_template_definitions(self) -> list[TemplateDefinition]:
        templates = await self.get_active_templates()
        return [TemplateDefinition.model_validate(t.config_json) for t in templates]

    async def get_latest_by_key(self, template_key: str) -> TemplateDefinition | None:
        stmt: Select[tuple[TemplateORM]] = (
            select(TemplateORM)
            .where(TemplateORM.template_key == template_key, TemplateORM.is_active.is_(True))
            .order_by(TemplateORM.version.desc())
            .limit(1)
        )
        row = (await self._session.execute(stmt)).scalars().first()
        if row is None:
            return None
        return TemplateDefinition.model_validate(row.config_json)

    async def get_by_id(self, template_id: str) -> TemplateORM | None:
        stmt: Select[tuple[TemplateORM]] = select(TemplateORM).where(TemplateORM.id == template_id)
        row = (await self._session.execute(stmt)).scalars().first()
        return row

