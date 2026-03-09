from datetime import datetime, timezone
import pytest

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.template import TemplateDefinition, TemplateScene
from trend2video.domain.entities.trend import NormalizedTrend
from trend2video.domain.services.script_engine import ScriptEngine


@pytest.mark.asyncio
async def test_script_engine_generates_script():
    trend = NormalizedTrend(
        source="static",
        external_id="t1",
        trend_type="hashtag",
        title="Automation trend",
        region="US",
        industry=None,
        rank=None,
        heat=None,
        velocity=30.0,
        tags=["sales", "automation"],
        raw_payload={},
        discovered_at=datetime.now(timezone.utc),
    )
    template = TemplateDefinition(
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
    brand_ctx = BrandContext(
        product_name="LeadFlow",
        product_type="platform",
        audience=["sales"],
        pain_points=["slow lead response"],
        tone="direct",
        forbidden_topics=[],
        cta_style="short_direct",
        niche_tags=["sales"],
    )

    engine = ScriptEngine()
    script = await engine.generate(trend, template, brand_ctx)

    assert script.trend_id == trend.external_id
    assert script.template_id == template.id
    assert script.hook_text
    assert script.cta_text

