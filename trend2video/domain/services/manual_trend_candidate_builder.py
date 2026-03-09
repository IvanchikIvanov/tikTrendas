from __future__ import annotations

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.manual_trend import ManualTrendInput
from trend2video.domain.entities.manual_trend_reference import ManualTrendReference


class ManualTrendCandidateBuilder:
    def _candidate_type(self, trend: ManualTrendInput) -> str:
        text = " ".join([trend.title, trend.notes or "", *trend.manual_tags]).lower()
        if any(token in text for token in ("free", "promo", "offer", "discount")):
            return "offer_hook"
        if any(token in text for token in ("how", "guide", "tips", "tutorial")):
            return "education"
        return "pain_solution"

    def build_candidate(
        self,
        trend: ManualTrendInput,
        references: list[ManualTrendReference],
        brand_ctx: BrandContext,
    ) -> ContentCandidate:
        source_text = " ".join(
            [
                trend.title,
                trend.notes or "",
                *trend.reference_hook_texts,
                *trend.manual_tags,
                *(reference.hook_text or "" for reference in references),
                *(reference.notes or "" for reference in references),
            ]
        ).lower()
        niche_hits = sum(1 for tag in brand_ctx.niche_tags if tag.lower() in source_text)
        product_relevance_score = min(1.0, 0.35 + niche_hits * 0.2 + (0.15 if trend.manual_tags else 0.0))
        signal_score = min(
            1.0,
            0.3
            + min(0.3, len(trend.reference_hook_texts) * 0.1)
            + min(0.2, len(trend.related_video_urls) * 0.05)
            + (0.2 if trend.priority <= 2 else 0.05),
        )
        scriptability_score = min(
            1.0,
            0.4
            + (0.2 if trend.notes else 0.0)
            + min(0.2, len(trend.reference_hook_texts) * 0.08)
            + (0.1 if references else 0.0),
        )
        candidate_type = self._candidate_type(trend)
        lead_tag = next(iter(trend.manual_tags), next(iter(brand_ctx.niche_tags), "general"))
        recommended_angle = f"{lead_tag}/{candidate_type}/{trend.title.lower().replace(' ', '-')}"
        return ContentCandidate(
            manual_trend_input_id=trend.id,
            source_type="manual_trend",
            candidate_type=candidate_type,
            product_relevance_score=round(product_relevance_score, 4),
            signal_score=round(signal_score, 4),
            scriptability_score=round(scriptability_score, 4),
            recommended_angle=recommended_angle,
            metadata_json={
                "manual_trend": trend.model_dump(mode="json"),
                "references": [reference.model_dump(mode="json") for reference in references],
                "brand_context_tags": brand_ctx.niche_tags,
            },
        )
