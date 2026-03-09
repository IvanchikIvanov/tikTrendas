from __future__ import annotations

from typing import Type

from pydantic import BaseModel

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.integrations.llm.base import LLMClient


class FakeLLMClient(LLMClient):
    def __init__(self, brand_ctx: BrandContext | None = None) -> None:
        self._brand_ctx = brand_ctx

    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> dict:
        return {}

    async def generate_from_context(
        self,
        candidate: ContentCandidate,
        keyword_trend: KeywordTrend | None,
        related_videos: list[RelatedVideo],
        template: TemplateDefinition,
        brand_ctx: BrandContext,
        schema: Type[BaseModel],
    ) -> dict:
        candidate_meta = candidate.metadata_json or {}
        manual_context = candidate_meta.get("manual_trend", {})
        keyword_text = keyword_trend.keyword if keyword_trend is not None else (manual_context.get("title") or candidate.candidate_type)
        hashtags = []
        for tag in keyword_text.lower().split():
            if tag and not tag.startswith("#"):
                hashtags.append(f"#{tag}")
        for niche in brand_ctx.niche_tags:
            hashtag = f"#{niche}"
            if hashtag not in hashtags:
                hashtags.append(hashtag)

        overlay = next(
            (
                video.overlay_text
                for video in related_videos
                if video.overlay_text
            ),
            next(iter(manual_context.get("reference_hook_texts", [])), keyword_text),
        )
        hook = template.hooks[0] if template.hooks else f"{keyword_text} breakdown"
        data = {
            "content_candidate_id": str(candidate.id or candidate.keyword_trend_id or candidate.manual_trend_input_id or 0),
            "keyword_trend_id": str(keyword_trend.id) if keyword_trend is not None and keyword_trend.id is not None else None,
            "template_id": template.id,
            "hook_text": f"{hook}: {overlay}",
            "pain_text": brand_ctx.pain_points[0] if brand_ctx.pain_points else None,
            "solution_text": f"Use {brand_ctx.product_name} to simplify the workflow",
            "outcome_text": "Faster output and clearer hooks",
            "cta_text": "Comment DEMO for the workflow",
            "caption": (
                f"{brand_ctx.product_name}: build a video around '{keyword_text}' "
                f"using angle '{candidate.recommended_angle or candidate.candidate_type}'."
            ),
            "hashtags": hashtags[:10],
            "metadata": {
                "candidate_type": candidate.candidate_type,
                "source_type": candidate.source_type,
                "related_videos_count": len(related_videos),
                "tone": brand_ctx.tone,
            },
        }
        return schema.model_validate(data).model_dump(mode="json")
