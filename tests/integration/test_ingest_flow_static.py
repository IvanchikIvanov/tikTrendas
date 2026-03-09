import json
import os
from pathlib import Path

import pytest

from trend2video.core.config import get_settings
from trend2video.core.db import get_session_factory
from trend2video.domain.services.trend_normalizer import TrendNormalizer
from trend2video.integrations.tiktok.trend_source_static import StaticJsonTrendSource
from trend2video.persistence.repositories.trend_repository import TrendRepository


@pytest.mark.asyncio
async def test_ingest_flow_static(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    data = [
        {
            "source": "static",
            "external_id": "t1",
            "trend_type": "hashtag",
            "title": "Test",
            "region": "US",
            "tags": ["sales"],
        }
    ]
    json_path = tmp_path / "trends.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setenv("T2V_TREND_SOURCE", "static")
    monkeypatch.setenv("T2V_STATIC_TRENDS_PATH", str(json_path))

    # переинициализировать settings
    get_settings.cache_clear()  # type: ignore[attr-defined]

    source = StaticJsonTrendSource(TrendNormalizer(), path=str(json_path))
    session_factory = get_session_factory()

    async with session_factory() as session:
        repo = TrendRepository(session)
        trends = await source.fetch_new_trends()
        objs, summary = await repo.upsert_trends(trends)

        assert len(objs) == 1
        assert summary["inserted_count"] == 1

