from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.domain.entities.content_candidate import ContentCandidate, ContentCandidateStatus
from trend2video.persistence.models.content_candidate import ContentCandidateORM


class ContentCandidateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, orm: ContentCandidateORM) -> ContentCandidate:
        return ContentCandidate(
            id=orm.id,
            job_id=orm.job_id,
            keyword_trend_id=orm.keyword_trend_id,
            candidate_type=orm.candidate_type,
            product_relevance_score=orm.product_relevance_score,
            signal_score=orm.signal_score,
            scriptability_score=orm.scriptability_score,
            recommended_angle=orm.recommended_angle,
            status=orm.status,
            metadata_json=orm.metadata_json or {},
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    async def create_many(self, candidates: list[ContentCandidate]) -> list[ContentCandidate]:
        persisted: list[ContentCandidate] = []
        for candidate in candidates:
            orm = ContentCandidateORM(
                job_id=candidate.job_id,
                keyword_trend_id=candidate.keyword_trend_id,
                candidate_type=candidate.candidate_type,
                product_relevance_score=candidate.product_relevance_score,
                signal_score=candidate.signal_score,
                scriptability_score=candidate.scriptability_score,
                recommended_angle=candidate.recommended_angle,
                status=candidate.status.value if hasattr(candidate.status, "value") else str(candidate.status),
                metadata_json=candidate.metadata_json,
            )
            self._session.add(orm)
            await self._session.flush()
            persisted.append(self._to_entity(orm))
        await self._session.commit()
        return persisted

    async def list_for_job(self, job_id: int) -> Sequence[ContentCandidate]:
        stmt: Select[tuple[ContentCandidateORM]] = (
            select(ContentCandidateORM)
            .where(ContentCandidateORM.job_id == job_id)
            .order_by(ContentCandidateORM.scriptability_score.desc())
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]

    async def get_top_candidates(self, job_id: int, limit: int = 10) -> Sequence[ContentCandidate]:
        stmt: Select[tuple[ContentCandidateORM]] = (
            select(ContentCandidateORM)
            .where(ContentCandidateORM.job_id == job_id)
            .order_by(ContentCandidateORM.scriptability_score.desc(), ContentCandidateORM.signal_score.desc())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [self._to_entity(row) for row in rows]

    async def mark_status(self, candidate_id: int, status: ContentCandidateStatus | str) -> ContentCandidate | None:
        orm = await self._session.get(ContentCandidateORM, candidate_id)
        if orm is None:
            return None
        orm.status = status.value if hasattr(status, "value") else str(status)
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def get_by_id(self, candidate_id: int) -> ContentCandidate | None:
        orm = await self._session.get(ContentCandidateORM, candidate_id)
        return None if orm is None else self._to_entity(orm)
