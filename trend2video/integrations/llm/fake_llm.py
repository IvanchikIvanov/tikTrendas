from __future__ import annotations

from typing import Type

from pydantic import BaseModel

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.domain.entities.trend import NormalizedTrend
from trend2video.integrations.llm.base import LLMClient


class FakeLLMClient(LLMClient):
    """Детерминированный LLM-клиент для локальной разработки и тестов."""

    def __init__(
        self,
        brand_ctx: BrandContext | None = None,
    ) -> None:
        self._brand_ctx = brand_ctx

    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> dict:
        # Для Sprint 1 мы не парсим промпт, а полагаемся на явно переданные
        # структуры в ScriptEngine (trend/template/brand_ctx) и собираем
        # ответ по простым эвристикам.
        # ScriptEngine сам прокинет нужные значения в metadata.
        # Здесь оставляем минимальную заглушку: ScriptEngine будет
        # игнорировать prompt и не будет передавать сюда дополнительные данные.
        # Чтобы не ломать контракт, вернём пустой dict, который затем
        # будет заменён ScriptEngine-ом.
        return {}

    async def generate_from_context(
        self,
        trend: NormalizedTrend,
        template: TemplateDefinition,
        brand_ctx: BrandContext,
        schema: Type[BaseModel],
    ) -> dict:
        """Упрощённая генерация structured-ответа без разбора промпта."""

        hashtags = []
        for tag in (trend.tags or []):
            if tag and not tag.startswith("#"):
                hashtags.append(f"#{tag}")
        for niche in brand_ctx.niche_tags:
            ht = f"#{niche}"
            if ht not in hashtags:
                hashtags.append(ht)

        hook = template.hooks[0] if template.hooks else f"{trend.title} — быстрый разбор"
        caption = f"{brand_ctx.product_name}: как использовать тренд «{trend.title}» в нише {', '.join(brand_ctx.niche_tags) or 'бизнеса'}."

        data = {
            "trend_id": trend.external_id,
            "template_id": template.id,
            "hook_text": hook,
            "pain_text": "Клиент теряется на первом шаге" if "slow" in " ".join(brand_ctx.pain_points) else None,
            "solution_text": f"Используем {brand_ctx.product_name} для автоматизации" if brand_ctx.product_name else None,
            "outcome_text": "Больше обработанных лидов и меньше потерь",
            "cta_text": "Напиши ДЕМО в комментарии",
            "caption": caption,
            "hashtags": hashtags[:10],
            "metadata": {
                "tone": brand_ctx.tone,
                "variant": "A",
            },
        }
        return schema.model_validate(data).model_dump(mode="json")

