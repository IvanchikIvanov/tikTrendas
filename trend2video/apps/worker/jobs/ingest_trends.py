from __future__ import annotations

import asyncio

from trend2video.core.config import get_settings
from trend2video.core.db import get_session_factory
from trend2video.domain.services.trend_normalizer import TrendNormalizer
from trend2video.integrations.tiktok.trend_source_creative_center import CreativeCenterTrendSource
from trend2video.integrations.tiktok.trend_source_static import StaticJsonTrendSource
from trend2video.persistence.repositories.trend_repository import TrendRepository


async def run_ingest_job() -> None:
    settings = get_settings()
    session_factory = get_session_factory()

    normalizer = TrendNormalizer()
    if settings.trend_source == "creative_center":
        source = CreativeCenterTrendSource(normalizer=normalizer)
    else:
        source = StaticJsonTrendSource(normalizer=normalizer, path=settings.static_trends_path)

    async with session_factory() as session:
        repo = TrendRepository(session)
        trends = await source.fetch_new_trends()
        _, summary = await repo.upsert_trends(trends)
        print(f"Ingest summary: {summary}")


if __name__ == "__main__":
    asyncio.run(run_ingest_job())

