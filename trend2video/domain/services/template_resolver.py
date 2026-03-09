from __future__ import annotations

from typing import Iterable

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.template import TemplateDefinition


class TemplateResolver:
    def score_template(
        self,
        candidate: ContentCandidate,
        template: TemplateDefinition,
        brand_ctx: BrandContext,
    ) -> float:
        score = 0.0
        candidate_type = candidate.candidate_type.lower()
        recommended_angle = (candidate.recommended_angle or "").lower()
        template_tags = {tag.lower() for tag in template.tags}

        if candidate_type in template_tags:
            score += 0.3

        scene_ids = {scene.scene_id for scene in template.scene_plan}
        if {"hook", "cta"} <= scene_ids:
            score += 0.3
        if "pain" in scene_ids and "solution" in scene_ids:
            score += 0.2

        niche_lower = {tag.lower() for tag in brand_ctx.niche_tags}
        if template_tags & niche_lower:
            score += 0.2
        if any(tag in recommended_angle for tag in template_tags):
            score += 0.1
        return max(0.0, min(1.0, score))

    def pick_best(
        self,
        candidate: ContentCandidate,
        templates: Iterable[TemplateDefinition],
        brand_ctx: BrandContext,
        threshold: float = 0.3,
    ) -> TemplateDefinition | None:
        best_template: TemplateDefinition | None = None
        best_score = threshold
        for template in templates:
            if not template.active:
                continue
            score = self.score_template(candidate, template, brand_ctx)
            if score > best_score:
                best_score = score
                best_template = template
        return best_template
