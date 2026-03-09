from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trend2video.core.config import get_settings
from trend2video.domain.entities.trend import NormalizedTrend
from trend2video.domain.services.trend_normalizer import TrendNormalizer
from trend2video.integrations.tiktok.trend_source_base import TrendSource


class StaticJsonTrendSource(TrendSource):
    """Источник трендов из локального JSON-файла.

    Подходит для локальной разработки, CI и детерминированной отладки.
    """

    def __init__(self, normalizer: TrendNormalizer | None = None, path: str | None = None) -> None:
        settings = get_settings()
        self._path = Path(path or settings.static_trends_path)
        self._normalizer = normalizer or TrendNormalizer()

    async def fetch_new_trends(self) -> list[NormalizedTrend]:
        raw_items = self._load_raw_items()
        trends: list[NormalizedTrend] = []
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            # гарантируем наличие source/external_id хотя бы дефолтами
            raw.setdefault("source", raw.get("source") or "static_json")
            if "external_id" not in raw and "id" in raw:
                raw["external_id"] = raw["id"]
            trends.append(self._normalizer.normalize(raw))
        return trends

    def _load_raw_items(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        data = json.loads(self._path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            return [item for item in data["items"] if isinstance(item, dict)]
        return []

