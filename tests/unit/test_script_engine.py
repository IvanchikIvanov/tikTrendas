from __future__ import annotations

import pytest

from trend2video.core.config import get_settings
from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.template import TemplateDefinition, TemplateScene
from trend2video.domain.services.script_engine import ScriptEngine


@pytest.mark.asyncio
async def test_script_engine_generates_script_from_candidate() -> None:
    engine = ScriptEngine()
    candidate = ContentCandidate(
        id=1,
        job_id=1,
        keyword_trend_id=1,
        candidate_type="offer_hook",
        product_relevance_score=0.9,
        signal_score=0.8,
        scriptability_score=0.85,
        recommended_angle="ecommerce/ugc/free-delivery",
    )
    keyword = KeywordTrend(
        id=1,
        job_id=1,
        source="static",
        country="Belarus",
        time_window="7d",
        keyword="free delivery promo",
    )
    videos = [
        RelatedVideo(
            keyword_trend_id=1,
            source_platform="tiktok",
            source_url="https://example.com/video",
            overlay_text="free delivery this week",
        )
    ]
    template = TemplateDefinition(
        template_key="problem_solution_fastcut",
        version="v1",
        name="Problem Solution Fast Cut",
        duration_sec=18,
        aspect_ratio="9:16",
        hooks=["hook"],
        scene_plan=[
            TemplateScene(scene_id="hook", asset_type="ugc", asset_tag="x", duration_sec=2.0, text_slot="hook_text"),
            TemplateScene(scene_id="cta", asset_type="ugc", asset_tag="y", duration_sec=2.0, text_slot="cta_text"),
        ],
        tags=["offer_hook"],
        caption_policy={},
        active=True,
    )
    script = await engine.generate(candidate, keyword, videos, template, get_settings().brand_context)
    assert script.content_candidate_id == "1"
    assert script.template_id == template.id
    assert script.hook_text
