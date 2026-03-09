from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from trend2video.apps.api.main import app


@pytest.mark.asyncio
async def test_search_job_crud_flow() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post(
            "/search-jobs",
            json={
                "name": "BY_7d_top10_ecom",
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
        assert create_response.status_code == 200
        job_id = create_response.json()["id"]

        patch_response = await client.patch(f"/search-jobs/{job_id}", json={"top_keywords_limit": 5})
        assert patch_response.status_code == 200
        assert patch_response.json()["top_keywords_limit"] == 5

        list_response = await client.get("/search-jobs")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1


@pytest.mark.asyncio
async def test_search_job_create_rejects_unknown_source_type() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post(
            "/search-jobs",
            json={
                "name": "bad_source_job",
                "countries": ["Belarus"],
                "time_window": "7d",
                "source_types": ["tiktok_keyword_insights"],
            },
        )

        assert create_response.status_code == 422
