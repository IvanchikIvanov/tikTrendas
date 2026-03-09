from __future__ import annotations

import asyncio

from trend2video.core.config import get_settings
from trend2video.core.db import get_session_factory
from trend2video.domain.entities.content_candidate import ContentCandidateStatus
from trend2video.domain.services.script_engine import ScriptEngine
from trend2video.domain.services.template_resolver import TemplateResolver
from trend2video.persistence.repositories.content_candidate_repository import ContentCandidateRepository
from trend2video.persistence.repositories.keyword_trend_repository import KeywordTrendRepository
from trend2video.persistence.repositories.manual_trend_repository import ManualTrendRepository
from trend2video.persistence.repositories.related_video_repository import RelatedVideoRepository
from trend2video.persistence.repositories.script_repository import ScriptRepository
from trend2video.persistence.repositories.search_job_repository import SearchJobRepository
from trend2video.persistence.repositories.template_repository import TemplateRepository


async def run_generate_scripts(
    job_id: int | None = None,
    candidate_id: int | None = None,
    limit: int = 10,
) -> dict[str, int]:
    session_factory = get_session_factory()
    generated = 0
    engine = ScriptEngine()
    resolver = TemplateResolver()
    async with session_factory() as session:
        job_repo = SearchJobRepository(session)
        keyword_repo = KeywordTrendRepository(session)
        manual_repo = ManualTrendRepository(session)
        related_repo = RelatedVideoRepository(session)
        candidate_repo = ContentCandidateRepository(session)
        template_repo = TemplateRepository(session)
        script_repo = ScriptRepository(session)
        templates = await template_repo.get_active_template_definitions()
        if candidate_id is not None:
            candidates = [await candidate_repo.get_by_id(candidate_id)]
        else:
            jobs = [await job_repo.get_by_id(job_id)] if job_id is not None else list(await job_repo.list_active())
            candidates = []
            for job in jobs:
                if job is None:
                    continue
                candidates.extend(await candidate_repo.get_top_candidates(job.id, limit=limit))
        for candidate in candidates:
            if candidate is None:
                continue
            if await script_repo.get_by_candidate_id(candidate.id):
                continue
            keyword = None
            related_videos = []
            if candidate.keyword_trend_id is not None:
                keyword = await keyword_repo.get_by_id(candidate.keyword_trend_id)
                if keyword is None:
                    continue
                related_videos = list(await related_repo.list_for_keyword_trend(keyword.id))
            elif candidate.manual_trend_input_id is not None:
                manual_trend = await manual_repo.get_by_id(candidate.manual_trend_input_id)
                if manual_trend is None:
                    continue
                related_videos = manual_repo.as_related_videos(manual_trend)
            else:
                continue
            template = resolver.pick_best(candidate, templates, get_settings().brand_context)
            if template is None:
                continue
            tmpl_orm = await template_repo.get_by_id(template.id)
            if tmpl_orm is None:
                continue
            script = await engine.generate(candidate, keyword, related_videos, template, get_settings().brand_context)
            await script_repo.create_for_candidate(candidate, keyword, tmpl_orm, script)
            await candidate_repo.mark_status(candidate.id, ContentCandidateStatus.SCRIPT_GENERATED)
            generated += 1
    return {"scripts_generated": generated}


if __name__ == "__main__":
    asyncio.run(run_generate_scripts())
