from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from trend2video.apps.api.main import app


@pytest.mark.asyncio
async def test_manual_trend_to_review_and_publish_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_render(_render_job_id: int) -> dict[str, str | int]:
        return {"render_job_id": _render_job_id, "status": "queued"}

    monkeypatch.setattr("trend2video.apps.api.routes.renders.run_render_draft", fake_render)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_trend = await client.post(
            "/manual-trends",
            json={
                "title": "for free",
                "trend_type": "keyword",
                "country": "Belarus",
                "time_window": "7d",
                "notes": "adapt to free audit offer",
                "reference_hook_texts": ["try it for free", "get it for free"],
                "related_video_urls": ["https://www.tiktok.com/@demo/video/123"],
                "manual_tags": ["offer", "promo", "ecommerce"],
                "priority": 1,
                "references": [
                    {
                        "source_platform": "tiktok",
                        "source_url": "https://www.tiktok.com/@demo/video/123",
                        "hook_text": "try it for free",
                    }
                ],
            },
        )
        assert create_trend.status_code == 200
        trend_id = create_trend.json()["id"]

        build_candidate = await client.post(f"/manual-trends/{trend_id}/build-candidate")
        assert build_candidate.status_code == 200
        assert build_candidate.json()["content_candidates_built"] == 1

        trend_details = await client.get(f"/manual-trends/{trend_id}")
        assert trend_details.status_code == 200
        candidate_id = trend_details.json()["candidates"][0]["id"]

        generate_script = await client.post(f"/candidates/{candidate_id}/generate-script")
        assert generate_script.status_code == 200
        assert generate_script.json()["scripts_generated"] == 1

        scripts = await client.get("/scripts")
        assert scripts.status_code == 200
        script_id = scripts.json()[0]["id"]

        asset = await client.post(
            "/assets",
            json={"asset_type": "broll", "asset_tag": "product_closeup", "path": "/tmp/closeup.mp4"},
        )
        assert asset.status_code == 200
        asset2 = await client.post(
            "/assets",
            json={"asset_type": "ugc", "asset_tag": "frustration", "path": "/tmp/frustration.mp4"},
        )
        assert asset2.status_code == 200
        asset3 = await client.post(
            "/assets",
            json={"asset_type": "screenrec", "asset_tag": "demo_main", "path": "/tmp/demo.mp4"},
        )
        assert asset3.status_code == 200
        asset4 = await client.post(
            "/assets",
            json={"asset_type": "broll", "asset_tag": "logo_endcard", "path": "/tmp/endcard.mp4"},
        )
        assert asset4.status_code == 200

        create_render = await client.post("/renders", json={"script_id": script_id})
        assert create_render.status_code == 200
        render_job_id = create_render.json()["id"]

        create_review = await client.post(
            f"/renders/{render_job_id}/review-request",
            json={"channel_type": "manual_dashboard", "reviewer": "qa"},
        )
        assert create_review.status_code == 200
        review_id = create_review.json()["id"]

        approve_review = await client.post(
            f"/review-requests/{review_id}/approve",
            json={"reviewer": "qa", "review_comment": "ok"},
        )
        assert approve_review.status_code == 200
        assert approve_review.json()["status"] == "approved"

        create_publish = await client.post(
            f"/renders/{render_job_id}/publish-jobs",
            json={"target_platform": "tiktok", "payload_json": {"caption": "draft"}},
        )
        assert create_publish.status_code == 200

        publish_jobs = await client.get("/publish-jobs")
        assert publish_jobs.status_code == 200
        assert len(publish_jobs.json()) == 1
