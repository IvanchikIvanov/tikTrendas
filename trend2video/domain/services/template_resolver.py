from __future__ import annotations

from typing import Iterable

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.domain.entities.trend import NormalizedTrend


class TemplateResolver:
    """Выбор наилучшего шаблона под тренд."""

    def score_template(
        self,
        trend: NormalizedTrend,
        template: TemplateDefinition,
        brand_ctx: BrandContext,
    ) -> float:
        score = 0.0

        # Соответствие типу тренда
        if trend.trend_type in template.tags:
            score += 0.3

        # Наличие ключевых сцен
        scene_ids = {s.scene_id for s in template.scene_plan}
        if {"hook", "cta"} <= scene_ids:
            score += 0.3
        if "pain" in scene_ids and "solution" in scene_ids:
            score += 0.2

        # Индустрия / ниша
        tags_lower = {t.lower() for t in template.tags}
        niche_lower = {t.lower() for t in brand_ctx.niche_tags}
        if tags_lower & niche_lower:
            score += 0.2

        return max(0.0, min(1.0, score))

    def pick_best(
        self,
        trend: NormalizedTrend,
        templates: Iterable[TemplateDefinition],
        brand_ctx: BrandContext,
        threshold: float = 0.3,
    ) -> TemplateDefinition | None:
        best_template: TemplateDefinition | None = None
        best_score = threshold

        for template in templates:
            if not template.active:
                continue
            s = self.score_template(trend, template, brand_ctx)
            if s > best_score:
                best_score = s
                best_template = template

        return best_template

