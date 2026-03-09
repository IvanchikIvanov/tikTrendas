from __future__ import annotations

import asyncio

from trend2video.core.config import get_settings
from trend2video.core.db import get_session_factory
from trend2video.domain.entities.manual_trend import ManualTrendStatus
from trend2video.domain.services.manual_trend_candidate_builder import ManualTrendCandidateBuilder
from trend2video.persistence.repositories.content_candidate_repository import ContentCandidateRepository
from trend2video.persistence.repositories.manual_trend_repository import ManualTrendRepository


async def run_build_manual_candidates(manual_trend_id: int) -> dict[str, int]:
    session_factory = get_session_factory()
    builder = ManualTrendCandidateBuilder()
    async with session_factory() as session:
        manual_repo = ManualTrendRepository(session)
        candidate_repo = ContentCandidateRepository(session)
        trend = await manual_repo.get_by_id(manual_trend_id)
        if trend is None:
            return {"content_candidates_built": 0}
        references = list(await manual_repo.list_references(manual_trend_id))
        candidate = builder.build_candidate(trend, references, get_settings().brand_context)
        await candidate_repo.create_many([candidate])
        await manual_repo.update(manual_trend_id, status=ManualTrendStatus.CANDIDATE_BUILT)
    return {"content_candidates_built": 1}


if __name__ == "__main__":
    asyncio.run(run_build_manual_candidates(1))
