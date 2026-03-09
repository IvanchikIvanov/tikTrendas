from __future__ import annotations

import json
from pathlib import Path
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
        self._debug_html_path = Path("/tmp/creative_center_debug.html")

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
        region = json.dumps(self._region)
        await page.add_init_script(
            f"""
            (() => {{
                try {{
                    window.localStorage.setItem("creative_center_region", {region});
                }} catch (_) {{}}
            }})()
            """
        )
        await page.goto(self._url, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        body_text = (await page.locator("body").inner_text())[:1500]
        card_count = await page.evaluate(
            """
            () => {
              const selectors = [
                '[data-e2e="creativecenter-hashtag-card"]',
                '[data-e2e="creativecenter-video-card"]',
                '[data-e2e*="creativecenter"][data-e2e*="card"]',
                '[class*="Card"][class*="Item"]',
                '[class*="card"][class*="item"]',
                '[class*="rank"] [class*="card"]',
                '[class*="trend"] [class*="card"]',
                'a[href*="/creativecenter/"] article',
                'main article',
                'main [role="listitem"]',
                'main section > div > div',
              ];
              const cards = [];
              for (const selector of selectors) {
                for (const node of document.querySelectorAll(selector)) {
                  const text = (node.textContent || '').trim();
                  if (text.length < 20) continue;
                  if (cards.includes(node)) continue;
                  cards.push(node);
                }
              }
              return cards.length;
            }
            """
        )
        self._debug_html_path.write_text(await page.content(), encoding="utf-8")

        print("DEBUG final_url:", page.url)
        print("DEBUG title:", await page.title())
        print("DEBUG body snippet:", body_text)
        print("DEBUG matched_card_count:", card_count)
        print("DEBUG html_dump:", str(self._debug_html_path))

    async def _extract_raw_trends(self, page: Any) -> list[dict]:
        """Вытянуть список сырых трендов из DOM.

        Это базовый хрупкий парсер. При изменении вёрстки его можно заменить,
        сохранив контракт на возвращаемую структуру.
        """

        script = r"""
        () => {
          const items = [];
          const selectorGroups = [
            '[data-e2e="creativecenter-hashtag-card"]',
            '[data-e2e="creativecenter-video-card"]',
            '[data-e2e*="creativecenter"][data-e2e*="card"]',
            '[class*="Card"][class*="Item"]',
            '[class*="card"][class*="item"]',
            '[class*="rank"] [class*="card"]',
            '[class*="trend"] [class*="card"]',
            'a[href*="/creativecenter/"] article',
            'main article',
            'main [role="listitem"]'
          ];
          const cards = [];
          selectorGroups.forEach((selector) => {
            document.querySelectorAll(selector).forEach((card) => {
              const text = (card.textContent || '').trim();
              if (text.length < 20) return;
              if (cards.includes(card)) return;
              cards.push(card);
            });
          });
          console.log(`DEBUG matched cards in page.evaluate: ${cards.length}`);
          cards.forEach((card, idx) => {
            const titleEl = card.querySelector(
              [
                '[data-e2e="creativecenter-hashtag-name"]',
                '[data-e2e*="name"]',
                '[class*="title"]',
                '[class*="Title"]',
                'h1',
                'h2',
                'h3',
                'h4'
              ].join(', ')
            );
            const title = titleEl ? titleEl.textContent.trim() : `trend_${idx}`;
            const heatEl = card.querySelector(
              [
                '[data-e2e="creativecenter-heat-score"]',
                '[data-e2e*="heat"]',
                '[class*="heat"]',
                '[class*="Hot"]',
                '[class*="Popularity"]'
              ].join(', ')
            );
            const heatText = heatEl ? heatEl.textContent.trim() : null;
            const velocityEl = card.querySelector(
              [
                '[data-e2e="creativecenter-growth-score"]',
                '[data-e2e*="growth"]',
                '[data-e2e*="velocity"]',
                '[class*="growth"]',
                '[class*="velocity"]'
              ].join(', ')
            );
            const velocityText = velocityEl ? velocityEl.textContent.trim() : null;
            const rankEl = card.querySelector(
              [
                '[data-e2e="creativecenter-ranking"]',
                '[data-e2e="rank"]',
                '[data-e2e*="rank"]',
                '[class*="rank"]',
                '[class*="Rank"]'
              ].join(', ')
            );
            const rankText = rankEl ? rankEl.textContent.trim() : null;
            const hrefEl = card.querySelector('a[href]');
            const href = hrefEl ? hrefEl.getAttribute('href') : null;
            const dataId =
              card.getAttribute('data-id') ||
              card.getAttribute('data-item-id') ||
              card.getAttribute('data-e2e-id');
            let externalId = dataId || null;
            if (!externalId && href) {
              const absolute = href.startsWith('http') ? href : `https://www.tiktok.com${href}`;
              const match =
                absolute.match(/(?:hashtag|music|video)\/([^/?#]+)/i) ||
                absolute.match(/[?&](?:id|item_id|hashtag_id)=([^&#]+)/i);
              externalId = match ? match[1] : absolute;
            }
            if (!externalId) {
              externalId = `dom_${idx}_${title.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '')}`;
            }
            const regionMeta =
              document.querySelector('meta[name="region"]')?.getAttribute('content') ||
              document.documentElement.getAttribute('lang') ||
              null;
            const tags = [];
            card.querySelectorAll('a[href*="hashtag"]').forEach(a => {
              const t = a.textContent.trim();
              if (t) tags.push(t.replace('#', ''));
            });
            items.push({
              source: "tiktok_creative_center",
              external_id: externalId,
              trend_type: "hashtag",
              title,
              region: regionMeta,
              rank: rankText ? parseInt(rankText.replace(/[^0-9]/g, ''), 10) : null,
              heat: heatText ? parseFloat(heatText.replace(/[^0-9.]/g, '')) : null,
              velocity: velocityText ? parseFloat(velocityText.replace(/[^0-9.]/g, '')) : null,
              tags,
              creative_center_url: href,
            });
          });
          return items;
        }
        """
        raw_items = await page.evaluate(script)
        if not isinstance(raw_items, list):
            return []
        normalized_items: list[dict] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            item.setdefault("region", self._region)
            normalized_items.append(item)
        return normalized_items
