from __future__ import annotations

from textwrap import dedent

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.domain.entities.trend import NormalizedTrend


def build_script_prompt(trend: NormalizedTrend, template: TemplateDefinition, brand_ctx: BrandContext) -> str:
    """Собрать промпт для генерации структурированного скрипта."""

    scene_desc = ", ".join(f"{s.scene_id}:{s.text_slot}" for s in template.scene_plan)
    audience = ", ".join(brand_ctx.audience)
    pains = ", ".join(brand_ctx.pain_points)
    niche = ", ".join(brand_ctx.niche_tags)
    forbidden = ", ".join(brand_ctx.forbidden_topics)

    prompt = dedent(
        f"""
        Ты пишешь короткий сценарий для TikTok/shorts по тренду.

        БРЕНД:
        - Название: {brand_ctx.product_name}
        - Продукт: {brand_ctx.product_type}
        - Аудитория: {audience}
        - Основные боли: {pains}
        - Тон: {brand_ctx.tone}
        - CTA стиль: {brand_ctx.cta_style}
        - Ниша/теги: {niche}
        - Запрещённые темы: {forbidden}

        ТРЕНД:
        - source: {trend.source}
        - external_id: {trend.external_id}
        - type: {trend.trend_type}
        - title: {trend.title}
        - region: {trend.region}
        - industry: {trend.industry}
        - tags: {", ".join(trend.tags)}

        ШАБЛОН:
        - id: {template.id}
        - name: {template.name}
        - duration_sec: {template.duration_sec}
        - aspect_ratio: {template.aspect_ratio}
        - hooks: {", ".join(template.hooks)}
        - scene_plan (scene_id:text_slot): {scene_desc}

        ЗАДАЧА:
        Сгенерируй строго JSON-объект, совместимый со схемой GeneratedScript:
        {{
          "trend_id": "string",
          "template_id": "string",
          "hook_text": "string",
          "pain_text": "string | null",
          "solution_text": "string | null",
          "outcome_text": "string | null",
          "cta_text": "string",
          "caption": "string",
          "hashtags": ["string", ...],
          "metadata": {{}}
        }}

        Требования:
        - НЕ добавляй никаких комментариев, только чистый JSON.
        - Хэштеги должны быть релевантны тренду и бренду.
        - Соблюдай тон: {brand_ctx.tone}.
        - CTA должен соответствовать стилю: {brand_ctx.cta_style}.
        - Не используй запретные темы.
        - trend_id = "{trend.external_id}"
        - template_id = "{template.id}"
        """
    ).strip()
    return prompt

