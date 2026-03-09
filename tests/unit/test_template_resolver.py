from datetime import datetime, timezone

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.template import TemplateDefinition, TemplateScene
from trend2video.domain.entities.trend import NormalizedTrend
from trend2video.domain.services.template_resolver import TemplateResolver


def _trend() -> NormalizedTrend:
    return NormalizedTrend(
        source="static",
        external_id="t1",
        trend_type="hashtag",
        title="Test",
        region="US",
        industry=None,
        rank=None,
        heat=None,
        velocity=None,
        tags=["sales"],
        raw_payload={},
        discovered_at=datetime.now(timezone.utc),
    )


def _brand() -> BrandContext:
    return BrandContext(
        product_name="LeadFlow",
        product_type="platform",
        audience=["sales"],
        pain_points=["slow lead response"],
        tone="direct",
        forbidden_topics=[],
        cta_style="short_direct",
        niche_tags=["sales"],
    )


def test_template_resolver_picks_best():
    resolver = TemplateResolver()
    good = TemplateDefinition(
        template_key="good",
        version="v1",
        name="Good",
        duration_sec=10,
        aspect_ratio="9:16",
        hooks=["h"],
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
        tags=["hashtag", "sales"],
        active=True,
    )
    bad = TemplateDefinition(
        template_key="bad",
        version="v1",
        name="Bad",
        duration_sec=10,
        aspect_ratio="1:1",
        hooks=[],
        scene_plan=[],
        caption_policy={},
        tags=[],
        active=True,
    )

    best = resolver.pick_best(_trend(), [bad, good], _brand())
    assert best is not None
    assert best.template_key == "good"

