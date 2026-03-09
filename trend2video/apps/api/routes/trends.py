from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from trend2video.apps.api.deps import (
    get_brand_context,
    get_script_engine,
    get_template_repository,
    get_trend_repository,
    get_trend_scorer,
    get_trend_source,
)
from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.services.script_engine import ScriptEngine
from trend2video.domain.services.template_resolver import TemplateResolver
from trend2video.domain.services.trend_scorer import TrendScorer
from trend2video.integrations.tiktok.trend_source_base import TrendSource
from trend2video.persistence.repositories.script_repository import ScriptRepository
from trend2video.persistence.repositories.template_repository import TemplateRepository
from trend2video.persistence.repositories.trend_repository import TrendRepository
from trend2video.persistence.repositories.script_repository import ScriptRepository
from trend2video.apps.api.deps import get_script_repository
from trend2video.domain.services.template_resolver import TemplateResolver


router = APIRouter(prefix="/trends", tags=["trends"])


@router.post("/ingest")
async def ingest_trends(
    trend_source: TrendSource = Depends(get_trend_source),
    trend_repo: TrendRepository = Depends(get_trend_repository),
) -> dict[str, Any]:
    trends = await trend_source.fetch_new_trends()
    _, summary = await trend_repo.upsert_trends(trends)
    summary["total"] = len(trends)
    return summary


@router.post("/process")
async def process_trends(
    limit: int = Query(20, ge=1, le=200),
    force_regenerate: bool = Query(False),
    trend_repo: TrendRepository = Depends(get_trend_repository),
    template_repo: TemplateRepository = Depends(get_template_repository),
    script_repo: ScriptRepository = Depends(get_script_repository),
    brand_ctx: BrandContext = Depends(get_brand_context),
    scorer: TrendScorer = Depends(get_trend_scorer),
    engine: ScriptEngine = Depends(get_script_engine),
) -> dict[str, Any]:
    resolver = TemplateResolver()
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

        # domain NormalizedTrend построим из ORM raw_payload_json
        raw = dict(trend.raw_payload_json or {})
        raw.setdefault("source", trend.source)
        raw.setdefault("external_id", trend.external_id)
        from trend2video.domain.services.trend_normalizer import TrendNormalizer

        norm = TrendNormalizer().normalize(raw)

        try:
            score = scorer.score(norm, brand_ctx, templates)
            await trend_repo.update_score(trend.id, score)

            template = resolver.pick_best(norm, templates, brand_ctx)
            if template is None:
                continue

            gen = await engine.generate(norm, template, brand_ctx)

            # найти TemplateORM по id
            tmpl_orm = await template_repo.get_by_id(template.id)
            if tmpl_orm is None:
                continue

            await script_repo.create_script(trend, tmpl_orm, gen)
            with_script += 1
        except Exception:
            failed += 1
            # статус failed выставим явно
            from trend2video.domain.entities.trend import TrendStatus

            await trend_repo.mark_status(trend.id, TrendStatus.FAILED)

    return {
        "processed": processed,
        "with_script": with_script,
        "skipped_existing": skipped_existing,
        "failed": failed,
    }


@router.get("")
async def list_trends(
    trend_repo: TrendRepository = Depends(get_trend_repository),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    trends = await trend_repo.list_trends(status=status, limit=limit, offset=offset)
    return [
        {
            "id": t.id,
            "source": t.source,
            "external_id": t.external_id,
            "title": t.title,
            "score": t.score,
            "status": t.status,
            "discovered_at": t.discovered_at,
        }
        for t in trends
    ]

