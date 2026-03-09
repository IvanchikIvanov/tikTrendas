from __future__ import annotations

import asyncio

from trend2video.core.db import get_session_factory
from trend2video.integrations.tiktok.keyword_source_registry import build_keyword_insights_source_for_job
from trend2video.persistence.repositories.keyword_trend_repository import KeywordTrendRepository
from trend2video.persistence.repositories.related_video_repository import RelatedVideoRepository
from trend2video.persistence.repositories.search_job_repository import SearchJobRepository


async def run_collect_related_videos(job_id: int | None = None) -> dict[str, int]:
    session_factory = get_session_factory()
    collected = 0
    processed_jobs = 0
    async with session_factory() as session:
        job_repo = SearchJobRepository(session)
        keyword_repo = KeywordTrendRepository(session)
        related_repo = RelatedVideoRepository(session)
        jobs = [await job_repo.get_by_id(job_id)] if job_id is not None else list(await job_repo.list_active())
        for job in jobs:
            if job is None:
                continue
            source = build_keyword_insights_source_for_job(job.source_types)
            keywords = await keyword_repo.get_without_related_videos(job.id)
            for keyword in keywords:
                videos = await source.collect_related_videos(job, keyword)
                persisted = await related_repo.bulk_insert(videos)
                collected += len(persisted)
            processed_jobs += 1
    return {"jobs_processed": processed_jobs, "related_videos_collected": collected}


if __name__ == "__main__":
    asyncio.run(run_collect_related_videos())
