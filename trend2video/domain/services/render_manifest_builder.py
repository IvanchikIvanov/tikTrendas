from __future__ import annotations

from trend2video.domain.entities.asset import Asset
from trend2video.domain.entities.script import GeneratedScript
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.domain.services.asset_selector import AssetSelector


class RenderManifestBuilder:
    def __init__(self, selector: AssetSelector | None = None) -> None:
        self._selector = selector or AssetSelector()

    def build(
        self,
        script: GeneratedScript,
        template: TemplateDefinition,
        assets: list[Asset],
    ) -> dict:
        scenes: list[dict] = []
        for scene in template.scene_plan:
            asset = self._selector.pick_asset(assets, scene)
            scenes.append(
                {
                    "scene_id": scene.scene_id,
                    "asset_type": asset.asset_type,
                    "asset_tag": asset.asset_tag,
                    "asset_path": asset.path,
                    "duration_sec": scene.duration_sec,
                    "text": getattr(script, scene.text_slot, None),
                    "text_slot": scene.text_slot,
                }
            )
        return {
            "template_id": template.id,
            "resolution": {"width": 1080, "height": 1920},
            "fps": 30,
            "caption": script.caption,
            "hashtags": script.hashtags,
            "scenes": scenes,
        }
