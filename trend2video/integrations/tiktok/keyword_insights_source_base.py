from __future__ import annotations

from typing import Protocol

from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.search_job import TrendSearchJob


class KeywordInsightsSource(Protocol):
    async def collect_keyword_trends(self, job: TrendSearchJob) -> list[KeywordTrend]:
        ...

    async def collect_related_videos(
        self,
        job: TrendSearchJob,
        keyword_trend: KeywordTrend,
    ) -> list[RelatedVideo]:
        ...
