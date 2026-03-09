from __future__ import annotations

from typing import Protocol

from trend2video.domain.entities.trend import NormalizedTrend


class TrendSource(Protocol):
    """Абстракция источника трендов."""

    async def fetch_new_trends(self) -> list[NormalizedTrend]:
        """Получить новые тренды, нормализованные в NormalizedTrend."""

        ...

