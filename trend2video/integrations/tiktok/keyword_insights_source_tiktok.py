from __future__ import annotations

from trend2video.core.config import get_settings
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.search_job import TrendSearchJob
from trend2video.integrations.tiktok.keyword_insights_source_base import KeywordInsightsSource


class TikTokKeywordInsightsSource(KeywordInsightsSource):
    """Live adapter skeleton for TikTok Keyword Insights."""

    def __init__(self) -> None:
        self._settings = get_settings()

    async def collect_keyword_trends(self, job: TrendSearchJob) -> list[KeywordTrend]:
        # TODO: implement stable live collection from TikTok Keyword Insights.
        return []

    async def collect_related_videos(
        self,
        job: TrendSearchJob,
        keyword_trend: KeywordTrend,
    ) -> list[RelatedVideo]:
        # TODO: implement stable live collection of related videos.
        return []
