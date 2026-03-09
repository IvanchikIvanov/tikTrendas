from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.template import TemplateDefinition, TemplateScene
from trend2video.domain.entities.trend import NormalizedTrend
from trend2video.domain.services.trend_scorer import TrendScorer
from datetime import datetime, timezone


def _base_trend() -> NormalizedTrend:
    return NormalizedTrend(
        source="static",
        external_id="t1",
        trend_type="hashtag",
        title="Test",
        region="US",
        industry=None,
        rank=None,
        heat=None,
        velocity=50.0,
        tags=["sales", "automation"],
        raw_payload={},
        discovered_at=datetime.now(timezone.utc),
    )


def _brand_ctx() -> BrandContext:
    return BrandContext(
        product_name="LeadFlow",
        product_type="platform",
        audience=["sales"],
        pain_points=["slow lead response"],
        tone="direct",
        forbidden_topics=[],
        cta_style="short_direct",
        niche_tags=["sales", "automation"],
    )


def _templates() -> list[TemplateDefinition]:
    return [
        TemplateDefinition(
            template_key="problem_solution_fastcut",
            version="v1",
            name="Problem Solution Fast Cut",
            duration_sec=18,
            aspect_ratio="9:16",
            hooks=["hook"],
            scene_plan=[
                TemplateScene(
                    scene_id="hook",
                    asset_type="broll",
                    asset_tag="x",
                    duration_sec=2.0,
                    text_slot="hook_text",
                ),
                TemplateScene(
                    scene_id="cta",
                    asset_type="broll",
                    asset_tag="y",
                    duration_sec=2.0,
                    text_slot="cta_text",
                ),
            ],
            caption_policy={},
            tags=["hashtag"],
            active=True,
        )
    ]


def test_trend_scorer_score_range():
    scorer = TrendScorer()
    score = scorer.score(_base_trend(), _brand_ctx(), _templates())
    assert 0.0 <= score <= 1.0

