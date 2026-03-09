from __future__ import annotations

from typing import Iterable

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.domain.entities.trend import NormalizedTrend


class TrendScorer:
    """Сервис расчёта итогового score тренда."""

    def score(
        self,
        trend: NormalizedTrend,
        brand_ctx: BrandContext,
        templates: list[TemplateDefinition],
    ) -> float:
        v = self._calc_velocity(trend)
        niche = self._calc_niche_relevance(trend, brand_ctx)
        brand = self._calc_brand_fit(trend, brand_ctx)
        tmpl = self._calc_template_fit(trend, templates)
        feas = self._calc_production_feasibility(trend)

        raw = 0.35 * v + 0.25 * niche + 0.15 * brand + 0.15 * tmpl + 0.10 * feas
        return max(0.0, min(1.0, float(raw)))

    def _calc_velocity(self, trend: NormalizedTrend) -> float:
        v = trend.velocity
        if v is None:
            return 0.5
        # Простая нормализация: предполагаем разумный диапазон [0, 100]
        v_clamped = max(0.0, min(100.0, float(v)))
        return v_clamped / 100.0

    def _calc_niche_relevance(self, trend: NormalizedTrend, brand_ctx: BrandContext) -> float:
        tags_lower = {t.lower() for t in trend.tags}
        niche_lower = {t.lower() for t in brand_ctx.niche_tags}
        if not tags_lower or not niche_lower:
            return 0.4
        overlap = tags_lower & niche_lower
        if not overlap:
            return 0.2
        ratio = len(overlap) / len(niche_lower)
        return max(0.0, min(1.0, ratio))

    def _calc_brand_fit(self, trend: NormalizedTrend, brand_ctx: BrandContext) -> float:
        text = " ".join([trend.title] + trend.tags).lower()
        for forbidden in brand_ctx.forbidden_topics:
            if forbidden.lower() in text:
                return 0.0
        # если совпадает хотя бы одна боль с трендом — считаем хороший fit
        pain_hit = any(p.lower().split()[0] in text for p in brand_ctx.pain_points)
        return 0.8 if pain_hit else 0.5

    def _calc_template_fit(
        self,
        trend: NormalizedTrend,
        templates: Iterable[TemplateDefinition],
    ) -> float:
        if not templates:
            return 0.0
        scores: list[float] = []
        for t in templates:
            s = 0.0
            if trend.trend_type in (t.tags or []):
                s += 0.4
            if t.scene_plan:
                slot_ids = {s.text_slot for s in t.scene_plan}
                if {"hook_text", "cta_text"} <= slot_ids:
                    s += 0.4
            if t.aspect_ratio == "9:16":
                s += 0.2
            scores.append(min(1.0, s))
        return sum(scores) / len(scores) if scores else 0.0

    def _calc_production_feasibility(self, trend: NormalizedTrend) -> float:
        # MVP: чем короче теги/проще тематика, тем выше оценка
        avg_len = (
            sum(len(t) for t in trend.tags) / len(trend.tags) if trend.tags else 5.0
        )
        if avg_len <= 8:
            return 0.9
        if avg_len <= 16:
            return 0.7
        return 0.4

