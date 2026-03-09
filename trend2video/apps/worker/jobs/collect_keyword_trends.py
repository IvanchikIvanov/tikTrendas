from __future__ import annotations

import asyncio

from trend2video.core.db import get_session_factory
from trend2video.integrations.tiktok.keyword_source_registry import build_keyword_insights_source_for_job
from trend2video.persistence.repositories.keyword_trend_repository import KeywordTrendRepository
from trend2video.persistence.repositories.search_job_repository import SearchJobRepository


async def run_collect_keyword_trends(job_id: int | None = None) -> dict[str, int]:
    session_factory = get_session_factory()
    inserted = 0
    processed_jobs = 0
    async with session_factory() as session:
        job_repo = SearchJobRepository(session)
        keyword_repo = KeywordTrendRepository(session)
        jobs = [await job_repo.get_by_id(job_id)] if job_id is not None else list(await job_repo.list_active())
        for job in jobs:
            if job is None:
                continue
            source = build_keyword_insights_source_for_job(job.source_types)
            keywords = await source.collect_keyword_trends(job)
            persisted = await keyword_repo.bulk_upsert(keywords)
            inserted += len(persisted)
            processed_jobs += 1
    return {"jobs_processed": processed_jobs, "keyword_trends_collected": inserted}


if __name__ == "__main__":
    asyncio.run(run_collect_keyword_trends())
