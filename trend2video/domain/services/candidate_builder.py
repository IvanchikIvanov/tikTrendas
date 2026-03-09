from __future__ import annotations

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.services.keyword_trend_scorer import KeywordTrendScorer


class CandidateBuilder:
    def __init__(self, scorer: KeywordTrendScorer | None = None) -> None:
        self._scorer = scorer or KeywordTrendScorer()

    def _candidate_type(self, keyword: str) -> str:
        lowered = keyword.lower()
        if any(token in lowered for token in ("free", "discount", "sale", "promo")):
            return "offer_hook"
        if any(token in lowered for token in ("how", "guide", "tutorial", "tips")):
            return "education"
        return "pain_solution"

    def _recommended_angle(
        self,
        keyword_trend: KeywordTrend,
        related_videos: list[RelatedVideo],
        brand_ctx: BrandContext,
    ) -> str:
        keyword = keyword_trend.keyword.lower().replace(" ", "-")
        video_tags = {
            tag.lower()
            for video in related_videos
            for tag in (video.topic_tags_json + video.visual_tags_json)
            if tag
        }
        niche = next(iter(brand_ctx.niche_tags), "general")
        if "ugc" in video_tags:
            return f"{niche}/ugc/{keyword}"
        return f"{niche}/{self._candidate_type(keyword_trend.keyword)}/{keyword}"

    def build_candidates(
        self,
        job_id: int,
        keyword_trend: KeywordTrend,
        related_videos: list[RelatedVideo],
        brand_ctx: BrandContext,
    ) -> list[ContentCandidate]:
        scores = self._scorer.score(keyword_trend, brand_ctx)
        overlay_hits = [
            video.overlay_text
            for video in related_videos
            if video.overlay_text and any(tag.lower() in video.overlay_text.lower() for tag in brand_ctx.niche_tags)
        ]
        scriptability = min(
            1.0,
            scores["overall_score"] * 0.6
            + (0.2 if related_videos else 0.0)
            + (0.2 if overlay_hits else 0.0),
        )
        return [
            ContentCandidate(
                job_id=job_id,
                keyword_trend_id=keyword_trend.id or 0,
                candidate_type=self._candidate_type(keyword_trend.keyword),
                product_relevance_score=scores["product_relevance_score"],
                signal_score=scores["signal_score"],
                scriptability_score=round(scriptability, 4),
                recommended_angle=self._recommended_angle(keyword_trend, related_videos, brand_ctx),
                metadata_json={
                    "keyword": keyword_trend.keyword,
                    "country": keyword_trend.country,
                    "matched_overlays": overlay_hits,
                    "related_videos_count": len(related_videos),
                    "score_breakdown": scores,
                },
            )
        ]
