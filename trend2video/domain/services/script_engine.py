from __future__ import annotations

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.script import GeneratedScript
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.domain.entities.trend import NormalizedTrend
from trend2video.integrations.llm.base import LLMClient
from trend2video.integrations.llm.fake_llm import FakeLLMClient
from trend2video.integrations.llm.prompt_builder import build_script_prompt


class ScriptEngine:
    """Генератор структурированного скрипта поверх LLM-клиента."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or FakeLLMClient()

    async def generate(
        self,
        trend: NormalizedTrend,
        template: TemplateDefinition,
        brand_ctx: BrandContext,
    ) -> GeneratedScript:
        """
        Сгенерировать структуру скрипта строго как GeneratedScript.

        Для FakeLLMClient используется отдельный путь с generate_from_context,
        чтобы не парсить промпт. Для реального LLM-клиента будет использован
        текстовый промпт.
        """

        if isinstance(self._llm, FakeLLMClient):
            raw = await self._llm.generate_from_context(trend, template, brand_ctx, GeneratedScript)
            return GeneratedScript.model_validate(raw)

        prompt = build_script_prompt(trend, template, brand_ctx)
        raw = await self._llm.generate_structured(prompt, GeneratedScript)
        return GeneratedScript.model_validate(raw)

