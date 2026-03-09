from __future__ import annotations

import asyncio

from trend2video.core.config import get_settings
from trend2video.core.db import get_session_factory
from trend2video.domain.services.candidate_builder import CandidateBuilder
from trend2video.persistence.repositories.content_candidate_repository import ContentCandidateRepository
from trend2video.persistence.repositories.keyword_trend_repository import KeywordTrendRepository
from trend2video.persistence.repositories.related_video_repository import RelatedVideoRepository
from trend2video.persistence.repositories.search_job_repository import SearchJobRepository


async def run_build_content_candidates(job_id: int | None = None) -> dict[str, int]:
    session_factory = get_session_factory()
    built = 0
    processed_jobs = 0
    builder = CandidateBuilder()
    async with session_factory() as session:
        job_repo = SearchJobRepository(session)
        keyword_repo = KeywordTrendRepository(session)
        related_repo = RelatedVideoRepository(session)
        candidate_repo = ContentCandidateRepository(session)
        jobs = [await job_repo.get_by_id(job_id)] if job_id is not None else list(await job_repo.list_active())
        for job in jobs:
            if job is None:
                continue
            ready_keywords = await keyword_repo.list_candidate_ready(job.id)
            for keyword in ready_keywords:
                related_videos = list(await related_repo.list_for_keyword_trend(keyword.id))
                candidates = builder.build_candidates(job.id, keyword, related_videos, get_settings().brand_context)
                persisted = await candidate_repo.create_many(candidates)
                built += len(persisted)
            processed_jobs += 1
    return {"jobs_processed": processed_jobs, "content_candidates_built": built}


if __name__ == "__main__":
    asyncio.run(run_build_content_candidates())
