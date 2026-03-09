from __future__ import annotations

from textwrap import dedent

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.template import TemplateDefinition


def build_script_prompt(
    candidate: ContentCandidate,
    keyword_trend: KeywordTrend,
    related_videos: list[RelatedVideo],
    template: TemplateDefinition,
    brand_ctx: BrandContext,
) -> str:
    scene_desc = ", ".join(f"{scene.scene_id}:{scene.text_slot}" for scene in template.scene_plan)
    overlays = " | ".join(video.overlay_text or "" for video in related_videos if video.overlay_text)
    transcripts = " | ".join(video.transcript or "" for video in related_videos if video.transcript)
    return dedent(
        f"""
        Build a short-form video script.

        BRAND:
        - product_name: {brand_ctx.product_name}
        - product_type: {brand_ctx.product_type}
        - audience: {", ".join(brand_ctx.audience)}
        - pain_points: {", ".join(brand_ctx.pain_points)}
        - tone: {brand_ctx.tone}
        - cta_style: {brand_ctx.cta_style}
        - niche_tags: {", ".join(brand_ctx.niche_tags)}

        CANDIDATE:
        - content_candidate_id: {candidate.id}
        - candidate_type: {candidate.candidate_type}
        - recommended_angle: {candidate.recommended_angle}
        - signal_score: {candidate.signal_score}
        - product_relevance_score: {candidate.product_relevance_score}

        KEYWORD TREND:
        - keyword: {keyword_trend.keyword}
        - country: {keyword_trend.country}
        - time_window: {keyword_trend.time_window}
        - popularity_change: {keyword_trend.popularity_change}
        - industry: {keyword_trend.industry}
        - objective: {keyword_trend.objective}

        RELATED VIDEOS:
        - overlays: {overlays}
        - transcripts: {transcripts}
        - urls: {", ".join(video.source_url for video in related_videos)}

        TEMPLATE:
        - template_id: {template.id}
        - hooks: {", ".join(template.hooks)}
        - scene_plan: {scene_desc}

        Return only JSON compatible with GeneratedScript.
        """
    ).strip()
