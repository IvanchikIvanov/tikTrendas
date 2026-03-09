from __future__ import annotations

from trend2video.domain.entities.asset import Asset
from trend2video.domain.entities.template import TemplateScene


class AssetSelector:
    def pick_asset(self, assets: list[Asset], scene: TemplateScene) -> Asset:
        exact = [asset for asset in assets if asset.asset_type == scene.asset_type and asset.asset_tag == scene.asset_tag]
        if exact:
            return exact[0]
        fallback = [asset for asset in assets if asset.asset_type == scene.asset_type]
        if fallback:
            return fallback[0]
        raise ValueError(f"No active asset for type={scene.asset_type} tag={scene.asset_tag}")
