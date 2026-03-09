from __future__ import annotations

from trend2video.core.config import get_settings
from trend2video.domain.entities.manual_trend import ManualTrendInput
from trend2video.domain.entities.manual_trend_reference import ManualTrendReference
from trend2video.domain.services.manual_trend_candidate_builder import ManualTrendCandidateBuilder


def test_manual_trend_candidate_builder_uses_manual_context() -> None:
    builder = ManualTrendCandidateBuilder()
    trend = ManualTrendInput(
        id=7,
        title="try it for free",
        trend_type="keyword",
        country="Belarus",
        time_window="7d",
        notes="adapt for ecommerce free audit angle",
        reference_hook_texts=["try it for free", "get it for free"],
        related_video_urls=["https://example.com/1"],
        manual_tags=["offer", "ecommerce"],
        priority=1,
    )
    references = [
        ManualTrendReference(
            manual_trend_input_id=7,
            source_platform="tiktok",
            source_url="https://example.com/1",
            hook_text="try it for free",
        )
    ]
    candidate = builder.build_candidate(trend, references, get_settings().brand_context)
    assert candidate.source_type == "manual_trend"
    assert candidate.manual_trend_input_id == 7
    assert candidate.candidate_type == "offer_hook"
    assert candidate.metadata_json["manual_trend"]["title"] == "try it for free"
