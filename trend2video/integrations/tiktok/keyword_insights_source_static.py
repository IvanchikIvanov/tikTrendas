from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from trend2video.core.config import get_settings
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.search_job import TrendSearchJob
from trend2video.integrations.tiktok.keyword_insights_source_base import KeywordInsightsSource
from trend2video.integrations.tiktok.schemas import KeywordInsightsRow


class StaticKeywordInsightsSource(KeywordInsightsSource):
    def __init__(self, path: str | None = None) -> None:
        settings = get_settings()
        self._path = Path(path or settings.static_keyword_insights_path)

    def _load(self) -> dict:
        return json.loads(self._path.read_text(encoding="utf-8"))

    async def collect_keyword_trends(self, job: TrendSearchJob) -> list[KeywordTrend]:
        payload = self._load()
        rows = [KeywordInsightsRow.model_validate(item) for item in payload.get("keywords", [])]
        items: list[KeywordTrend] = []
        for row in rows:
            if row.country not in job.countries:
                continue
            if row.time_window != job.time_window:
                continue
            if row.popularity_change is not None and row.popularity_change < job.min_popularity_change:
                continue
            items.append(
                KeywordTrend(
                    job_id=job.id or 0,
                    source="static_keyword_insights",
                    country=row.country,
                    time_window=row.time_window,
                    keyword=row.keyword,
                    rank=row.rank,
                    popularity=row.popularity,
                    popularity_change=row.popularity_change,
                    ctr=row.ctr,
                    keyword_type=row.keyword_type,
                    industry=row.industry,
                    objective=row.objective,
                    details_url=row.details_url,
                    collected_at=datetime.now(timezone.utc),
                    raw_payload_json=row.model_dump(mode="json"),
                )
            )
            if len(items) >= job.top_keywords_limit:
                break
        return items

    async def collect_related_videos(
        self,
        job: TrendSearchJob,
        keyword_trend: KeywordTrend,
    ) -> list[RelatedVideo]:
        payload = self._load()
        rows = [KeywordInsightsRow.model_validate(item) for item in payload.get("keywords", [])]
        items: list[RelatedVideo] = []
        for row in rows:
            if row.keyword != keyword_trend.keyword or row.country != keyword_trend.country:
                continue
            for raw_video in row.related_videos[: job.related_videos_per_keyword]:
                items.append(
                    RelatedVideo(
                        keyword_trend_id=keyword_trend.id or 0,
                        source_platform=raw_video.get("source_platform", "tiktok"),
                        source_url=raw_video["source_url"],
                        creator_name=raw_video.get("creator_name"),
                        thumbnail_url=raw_video.get("thumbnail_url"),
                        storage_path=raw_video.get("storage_path"),
                        overlay_text=raw_video.get("overlay_text"),
                        transcript=raw_video.get("transcript"),
                        duration_sec=raw_video.get("duration_sec"),
                        visual_tags_json=raw_video.get("visual_tags_json", []),
                        topic_tags_json=raw_video.get("topic_tags_json", []),
                        metadata_json=raw_video.get("metadata_json", {}),
                    )
                )
            break
        return items
