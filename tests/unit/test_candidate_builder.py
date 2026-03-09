from __future__ import annotations

from trend2video.core.config import get_settings
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.services.candidate_builder import CandidateBuilder


def test_candidate_builder_uses_keyword_and_related_videos() -> None:
    builder = CandidateBuilder()
    keyword = KeywordTrend(
        id=10,
        job_id=1,
        source="static",
        country="Belarus",
        time_window="7d",
        keyword="free delivery promo",
        popularity=300,
        popularity_change=70,
    )
    related_videos = [
        RelatedVideo(
            keyword_trend_id=10,
            source_platform="tiktok",
            source_url="https://example.com/video",
            overlay_text="free delivery for all orders",
            visual_tags_json=["ugc"],
            topic_tags_json=["ecommerce"],
        )
    ]
    candidates = builder.build_candidates(1, keyword, related_videos, get_settings().brand_context)
    assert len(candidates) == 1
    assert candidates[0].candidate_type == "offer_hook"
    assert candidates[0].scriptability_score > 0
