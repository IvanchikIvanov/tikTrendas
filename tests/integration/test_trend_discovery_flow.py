from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from trend2video.apps.api.main import app


@pytest.mark.asyncio
async def test_full_trend_discovery_flow() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_job = await client.post(
            "/search-jobs",
            json={
                "name": "BY_7d_ecom_flow",
                "countries": ["Belarus"],
                "time_window": "7d",
                "top_keywords_limit": 10,
                "related_videos_per_keyword": 2,
                "source_types": ["static"],
                "min_popularity_change": 20,
                "language": "ru",
                "product_tags": ["ecommerce", "delivery", "promo"],
                "mode": "new_and_growing",
                "is_active": True
            },
        )
        assert create_job.status_code == 200
        job_id = create_job.json()["id"]

        keywords_result = await client.post(f"/search-jobs/{job_id}/run-keywords")
        assert keywords_result.status_code == 200
        assert keywords_result.json()["keyword_trends_collected"] >= 1

        keyword_list = await client.get(f"/keyword-trends?job_id={job_id}")
        assert keyword_list.status_code == 200
        keywords = keyword_list.json()
        assert len(keywords) >= 1
        keyword_id = keywords[0]["id"]

        related_result = await client.post(f"/search-jobs/{job_id}/run-related-videos")
        assert related_result.status_code == 200
        assert related_result.json()["related_videos_collected"] >= 1

        related_list = await client.get(f"/related-videos?keyword_trend_id={keyword_id}")
        assert related_list.status_code == 200
        assert len(related_list.json()) >= 1

        candidates_result = await client.post(f"/search-jobs/{job_id}/build-candidates")
        assert candidates_result.status_code == 200
        assert candidates_result.json()["content_candidates_built"] >= 1

        candidate_list = await client.get(f"/candidates?job_id={job_id}")
        assert candidate_list.status_code == 200
        candidates = candidate_list.json()
        assert len(candidates) >= 1
        candidate_id = candidates[0]["id"]

        scripts_result = await client.post(f"/candidates/{candidate_id}/generate-script")
        assert scripts_result.status_code == 200
        assert scripts_result.json()["scripts_generated"] == 1

        scripts_list = await client.get("/scripts")
        assert scripts_list.status_code == 200
        scripts = scripts_list.json()
        assert len(scripts) == 1
        assert scripts[0]["content_candidate_id"] == candidate_id
