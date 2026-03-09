from __future__ import annotations

import asyncio
from typing import Any

from trend2video.core.config import get_settings
from trend2video.core.db import get_session_factory
from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.trend import TrendStatus
from trend2video.domain.services.script_engine import ScriptEngine
from trend2video.domain.services.template_resolver import TemplateResolver
from trend2video.domain.services.trend_normalizer import TrendNormalizer
from trend2video.domain.services.trend_scorer import TrendScorer
from trend2video.integrations.llm.fake_llm import FakeLLMClient
from trend2video.persistence.repositories.script_repository import ScriptRepository
from trend2video.persistence.repositories.template_repository import TemplateRepository
from trend2video.persistence.repositories.trend_repository import TrendRepository


async def run_process_job(limit: int = 20, force_regenerate: bool = False) -> dict[str, Any]:
    settings = get_settings()
    brand_ctx: BrandContext = settings.brand_context
    session_factory = get_session_factory()

    async with session_factory() as session:
        trend_repo = TrendRepository(session)
        template_repo = TemplateRepository(session)
        script_repo = ScriptRepository(session)

        scorer = TrendScorer()
        resolver = TemplateResolver()
        engine = ScriptEngine(FakeLLMClient(brand_ctx))
        normalizer = TrendNormalizer()

        unprocessed = await trend_repo.get_unprocessed_trends(limit=limit)
        templates = await template_repo.get_active_template_definitions()

        processed = 0
        with_script = 0
        skipped_existing = 0
        failed = 0

        for trend in unprocessed:
            processed += 1
            if not force_regenerate and await script_repo.exists_for_trend(trend.id):
                skipped_existing += 1
                continue

            raw = dict(trend.raw_payload_json or {})
            raw.setdefault("source", trend.source)
            raw.setdefault("external_id", trend.external_id)
            norm = normalizer.normalize(raw)

            try:
                score = scorer.score(norm, brand_ctx, templates)
                await trend_repo.update_score(trend.id, score)

                template = resolver.pick_best(norm, templates, brand_ctx)
                if template is None:
                    continue

                gen = await engine.generate(norm, template, brand_ctx)
                tmpl_orm = await template_repo.get_by_id(template.id)
                if tmpl_orm is None:
                    continue

                await script_repo.create_script(trend, tmpl_orm, gen)
                await trend_repo.mark_status(trend.id, TrendStatus.SCRIPT_GENERATED)
                with_script += 1
            except Exception:
                failed += 1
                await trend_repo.mark_status(trend.id, TrendStatus.FAILED)

        summary = {
            "processed": processed,
            "with_script": with_script,
            "skipped_existing": skipped_existing,
            "failed": failed,
        }
        print(f"Process summary: {summary}")
        return summary


if __name__ == "__main__":
    asyncio.run(run_process_job())

