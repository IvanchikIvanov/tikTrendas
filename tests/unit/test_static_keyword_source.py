from __future__ import annotations

import pytest

from trend2video.domain.entities.search_job import TrendSearchJob
from trend2video.integrations.tiktok.keyword_insights_source_static import StaticKeywordInsightsSource


@pytest.mark.asyncio
async def test_static_keyword_source_parses_keywords_and_related_videos() -> None:
    source = StaticKeywordInsightsSource(path="/root/Trendas/tikTrendas/data/static_keyword_insights.json")
    job = TrendSearchJob(
        id=1,
        name="BY_7d_top10_ecom",
        countries=["Belarus"],
        time_window="7d",
        top_keywords_limit=10,
        related_videos_per_keyword=2,
        source_types=["static"],
        min_popularity_change=20,
        language="ru",
        product_tags=["ecommerce"],
    )
    keywords = await source.collect_keyword_trends(job)
    assert len(keywords) >= 1
    keywords[0].id = 1
    related_videos = await source.collect_related_videos(job, keywords[0])
    assert len(related_videos) >= 1
