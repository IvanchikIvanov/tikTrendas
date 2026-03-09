from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.core.db import get_session_factory
from trend2video.domain.entities.trend import NormalizedTrend
from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.template import TemplateDefinition, TemplateScene
from trend2video.domain.services.trend_normalizer import TrendNormalizer
from trend2video.apps.worker.jobs.process_trends import run_process_job
from trend2video.persistence.repositories.trend_repository import TrendRepository
from trend2video.persistence.models.template import TemplateORM
from trend2video.domain.entities.brand import BrandContext


@pytest.mark.asyncio
async def test_process_flow_creates_script():
    session_factory = get_session_factory()
    async with session_factory() as session:  # type: AsyncSession
        # подготовим один тренд
        repo = TrendRepository(session)
        raw = {
            "source": "static",
            "external_id": "t1",
            "trend_type": "hashtag",
            "title": "Automation trend",
            "region": "US",
            "tags": ["sales", "automation"],
            "discovered_at": datetime.now(timezone.utc).isoformat(),
        }
        trend = TrendNormalizer().normalize(raw)
        await repo.upsert_trends([trend])

        # подготовим один шаблон
        tdef = TemplateDefinition(
            template_key="problem_solution_fastcut",
            version="v1",
            name="Problem Solution Fast Cut",
            duration_sec=18,
            aspect_ratio="9:16",
            hooks=["hook"],
            scene_plan=[
                TemplateScene(
                    scene_id="hook",
                    asset_type="broll",
                    asset_tag="x",
                    duration_sec=2.0,
                    text_slot="hook_text",
                ),
                TemplateScene(
                    scene_id="cta",
                    asset_type="broll",
                    asset_tag="y",
                    duration_sec=2.0,
                    text_slot="cta_text",
                ),
            ],
            caption_policy={},
            tags=["hashtag"],
            active=True,
        )
        tmpl = TemplateORM(
            id=tdef.id,
            template_key=tdef.template_key,
            version=tdef.version,
            config_json=tdef.model_dump(mode="json"),
            is_active=True,
        )
        session.add(tmpl)
        await session.commit()

    summary = await run_process_job(limit=10, force_regenerate=False)
    assert summary["with_script"] >= 1

