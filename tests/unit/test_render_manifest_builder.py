from __future__ import annotations

from trend2video.domain.entities.asset import Asset
from trend2video.domain.entities.script import GeneratedScript
from trend2video.domain.entities.template import TemplateDefinition, TemplateScene
from trend2video.domain.services.render_manifest_builder import RenderManifestBuilder


def test_render_manifest_builder_matches_scenes_to_assets() -> None:
    builder = RenderManifestBuilder()
    script = GeneratedScript(
        content_candidate_id="1",
        template_id="problem_solution_fastcut_v1",
        hook_text="Hook",
        pain_text="Pain",
        solution_text="Solution",
        cta_text="CTA",
        caption="Caption",
    )
    template = TemplateDefinition(
        template_key="problem_solution_fastcut",
        version="v1",
        name="Problem Solution Fast Cut",
        duration_sec=18,
        aspect_ratio="9:16",
        hooks=["Hook"],
        scene_plan=[
            TemplateScene(scene_id="hook", asset_type="broll", asset_tag="product_closeup", duration_sec=2.0, text_slot="hook_text"),
            TemplateScene(scene_id="cta", asset_type="ugc", asset_tag="face_cam", duration_sec=2.0, text_slot="cta_text"),
        ],
    )
    assets = [
        Asset(asset_type="broll", asset_tag="product_closeup", path="/tmp/a.mp4"),
        Asset(asset_type="ugc", asset_tag="face_cam", path="/tmp/b.mp4"),
    ]
    manifest = builder.build(script, template, assets)
    assert manifest["template_id"] == template.id
    assert manifest["scenes"][0]["asset_path"] == "/tmp/a.mp4"
    assert manifest["scenes"][1]["text"] == "CTA"
