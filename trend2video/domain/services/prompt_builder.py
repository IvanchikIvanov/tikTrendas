from __future__ import annotations

from textwrap import dedent

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.template import TemplateDefinition


def build_script_prompt(
    candidate: ContentCandidate,
    keyword_trend: KeywordTrend | None,
    related_videos: list[RelatedVideo],
    template: TemplateDefinition,
    brand_ctx: BrandContext,
) -> str:
    scene_desc = ", ".join(f"{scene.scene_id}:{scene.text_slot}" for scene in template.scene_plan)
    overlays = " | ".join(video.overlay_text or "" for video in related_videos if video.overlay_text)
    transcripts = " | ".join(video.transcript or "" for video in related_videos if video.transcript)
    candidate_meta = candidate.metadata_json or {}
    manual_context = candidate_meta.get("manual_trend", {})
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
        - source_type: {candidate.source_type}
        - candidate_type: {candidate.candidate_type}
        - recommended_angle: {candidate.recommended_angle}
        - signal_score: {candidate.signal_score}
        - product_relevance_score: {candidate.product_relevance_score}

        KEYWORD TREND:
        - keyword: {keyword_trend.keyword if keyword_trend else manual_context.get("title")}
        - country: {keyword_trend.country if keyword_trend else manual_context.get("country")}
        - time_window: {keyword_trend.time_window if keyword_trend else manual_context.get("time_window")}
        - popularity_change: {keyword_trend.popularity_change if keyword_trend else None}
        - industry: {keyword_trend.industry if keyword_trend else None}
        - objective: {keyword_trend.objective if keyword_trend else None}

        MANUAL TREND:
        - title: {manual_context.get("title")}
        - notes: {manual_context.get("notes")}
        - reference_hook_texts: {", ".join(manual_context.get("reference_hook_texts", []))}
        - manual_tags: {", ".join(manual_context.get("manual_tags", []))}
        - related_video_urls: {", ".join(manual_context.get("related_video_urls", []))}

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
