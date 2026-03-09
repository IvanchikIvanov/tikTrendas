from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.script import GeneratedScript
from trend2video.persistence.models.script import ScriptORM
from trend2video.persistence.models.template import TemplateORM


class ScriptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_for_candidate(
        self,
        candidate: ContentCandidate,
        keyword_trend: KeywordTrend | None,
        template: TemplateORM,
        script: GeneratedScript,
    ) -> ScriptORM:
        obj = ScriptORM(
            content_candidate_id=candidate.id,
            keyword_trend_id=keyword_trend.id if keyword_trend is not None else None,
            template_id=template.id,
            script_json=script.model_dump(mode="json"),
        )
        self._session.add(obj)
        await self._session.commit()
        await self._session.refresh(obj)
        return obj

    async def get_by_candidate_id(self, candidate_id: int) -> ScriptORM | None:
        stmt: Select[tuple[ScriptORM]] = select(ScriptORM).where(ScriptORM.content_candidate_id == candidate_id)
        return (await self._session.execute(stmt)).scalars().first()

    async def get_by_id(self, script_id: int) -> ScriptORM | None:
        stmt: Select[tuple[ScriptORM]] = select(ScriptORM).where(ScriptORM.id == script_id)
        return (await self._session.execute(stmt)).scalars().first()

    async def list_all(self, limit: int = 50, offset: int = 0) -> Sequence[ScriptORM]:
        stmt: Select[tuple[ScriptORM]] = (
            select(ScriptORM)
            .order_by(ScriptORM.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)
