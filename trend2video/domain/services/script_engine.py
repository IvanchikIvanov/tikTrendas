from __future__ import annotations

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.content_candidate import ContentCandidate
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.script import GeneratedScript
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.domain.services.prompt_builder import build_script_prompt
from trend2video.integrations.llm.base import LLMClient
from trend2video.integrations.llm.fake_llm import FakeLLMClient


class ScriptEngine:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client or FakeLLMClient()

    async def generate(
        self,
        candidate: ContentCandidate,
        keyword_trend: KeywordTrend,
        related_videos: list[RelatedVideo],
        template: TemplateDefinition,
        brand_ctx: BrandContext,
    ) -> GeneratedScript:
        if isinstance(self._llm, FakeLLMClient):
            raw = await self._llm.generate_from_context(
                candidate,
                keyword_trend,
                related_videos,
                template,
                brand_ctx,
                GeneratedScript,
            )
            return GeneratedScript.model_validate(raw)

        prompt = build_script_prompt(candidate, keyword_trend, related_videos, template, brand_ctx)
        raw = await self._llm.generate_structured(prompt, GeneratedScript)
        return GeneratedScript.model_validate(raw)
