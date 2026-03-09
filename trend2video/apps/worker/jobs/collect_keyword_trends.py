from __future__ import annotations

import asyncio

from trend2video.core.config import get_settings
from trend2video.core.db import get_session_factory
from trend2video.domain.entities.search_job import TrendSearchJob
from trend2video.integrations.tiktok.keyword_insights_source_base import KeywordInsightsSource
from trend2video.integrations.tiktok.keyword_insights_source_static import StaticKeywordInsightsSource
from trend2video.integrations.tiktok.keyword_insights_source_tiktok import TikTokKeywordInsightsSource
from trend2video.persistence.repositories.keyword_trend_repository import KeywordTrendRepository
from trend2video.persistence.repositories.search_job_repository import SearchJobRepository


def _build_source(job: TrendSearchJob) -> KeywordInsightsSource:
    settings = get_settings()
    if "tiktok_keyword_insights" in job.source_types:
        return TikTokKeywordInsightsSource()
    return StaticKeywordInsightsSource(path=settings.static_keyword_insights_path)


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
            source = _build_source(job)
            keywords = await source.collect_keyword_trends(job)
            persisted = await keyword_repo.bulk_upsert(keywords)
            inserted += len(persisted)
            processed_jobs += 1
    return {"jobs_processed": processed_jobs, "keyword_trends_collected": inserted}


if __name__ == "__main__":
    asyncio.run(run_collect_keyword_trends())
