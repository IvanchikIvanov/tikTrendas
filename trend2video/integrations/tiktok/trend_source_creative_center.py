from __future__ import annotations

from typing import Any

from playwright.async_api import async_playwright  # type: ignore[import]

from trend2video.core.config import get_settings
from trend2video.domain.entities.trend import NormalizedTrend
from trend2video.domain.services.trend_normalizer import TrendNormalizer
from trend2video.integrations.tiktok.trend_source_base import TrendSource


class CreativeCenterTrendSource(TrendSource):
    """Источник трендов из TikTok Creative Center через Playwright.

    MVP-реализация: один базовый путь парсинга, максимально изолированный
    внутри адаптера. При изменении вёрстки можно заменить/расширить парсер,
    не трогая остальную систему.
    """

    def __init__(self, normalizer: TrendNormalizer | None = None) -> None:
        settings = get_settings()
        self._url = settings.tiktok_creative_center_url
        self._region = settings.tiktok_region
        self._normalizer = normalizer or TrendNormalizer()

    async def fetch_new_trends(self) -> list[NormalizedTrend]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await self._open_page(page)
                raw_items = await self._extract_raw_trends(page)
            finally:
                await browser.close()

        trends: list[NormalizedTrend] = []
        for raw in raw_items:
            try:
                trends.append(self._normalizer.normalize(raw))
            except Exception:
                # TODO: логировать и считать как failed_raw
                continue
        return trends

    async def _open_page(self, page: Any) -> None:
        """Открыть страницу Creative Center и дождаться загрузки основных данных."""

        await page.goto(self._url, wait_until="networkidle")
        # TODO: возможно, понадобится выбор региона/фильтра по self._region
        await page.wait_for_timeout(3000)

    async def _extract_raw_trends(self, page: Any) -> list[dict]:
        """Вытянуть список сырых трендов из DOM.

        Это базовый хрупкий парсер. При изменении вёрстки его можно заменить,
        сохранив контракт на возвращаемую структуру.
        """

        script = """
        () => {
          const items = [];
          const cards = document.querySelectorAll('[data-e2e="creativecenter-hashtag-card"], [data-e2e="creativecenter-video-card"]');
          cards.forEach((card, idx) => {
            const titleEl = card.querySelector('[data-e2e="creativecenter-hashtag-name"], h3, h4');
            const title = titleEl ? titleEl.textContent.trim() : `trend_${idx}`;
            const heatEl = card.querySelector('[data-e2e="creativecenter-heat-score"]');
            const heatText = heatEl ? heatEl.textContent.trim() : null;
            const velocityEl = card.querySelector('[data-e2e="creativecenter-growth-score"]');
            const velocityText = velocityEl ? velocityEl.textContent.trim() : null;
            const tags = [];
            card.querySelectorAll('a[href*="hashtag"]').forEach(a => {
              const t = a.textContent.trim();
              if (t) tags.push(t.replace('#', ''));
            });
            items.push({
              source: "tiktok_creative_center",
              external_id: title,
              trend_type: "hashtag",
              title,
              region: "UNKNOWN",
              heat: heatText ? parseFloat(heatText.replace(/[^0-9.]/g, '')) : null,
              velocity: velocityText ? parseFloat(velocityText.replace(/[^0-9.]/g, '')) : null,
              tags,
            });
          });
          return items;
        }
        """
        raw_items = await page.evaluate(script)
        if not isinstance(raw_items, list):
            return []
        return [item for item in raw_items if isinstance(item, dict)]

