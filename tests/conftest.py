from __future__ import annotations

from pathlib import Path

import pytest
import pytest_asyncio

from trend2video.core.config import get_settings
from trend2video.core.db import get_engine, reset_db_state
from trend2video.persistence.models import (  # noqa: F401
    ContentCandidateORM,
    KeywordTrendORM,
    RelatedVideoORM,
    ScriptORM,
    TemplateORM,
    TrendORM,
    TrendSearchJobORM,
)
from trend2video.persistence.models.base import Base
from trend2video.scripts.seed_templates import seed


@pytest_asyncio.fixture(autouse=True)
async def setup_sqlite_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "trend2video_test.db"
    data_path = Path("/root/Trendas/tikTrendas/data/static_keyword_insights.json")
    monkeypatch.setenv("T2V_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("T2V_DEFAULT_KEYWORD_SOURCE_TYPE", "static")
    monkeypatch.setenv("T2V_STATIC_KEYWORD_INSIGHTS_PATH", str(data_path))
    get_settings.cache_clear()  # type: ignore[attr-defined]
    reset_db_state()

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await seed()
    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    reset_db_state()
    get_settings.cache_clear()  # type: ignore[attr-defined]
