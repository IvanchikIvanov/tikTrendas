from __future__ import annotations

import json

import httpx
import pytest

from trend2video.core.config import AppSettings, get_settings
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.search_job import TrendSearchJob
from trend2video.integrations.tiktok.keyword_insights_source_tiktok import (
    KEYWORD_INSIGHTS_API_URL,
    KEYWORD_SOURCE_NAME,
    TikTokKeywordInsightsSource,
)


SAMPLE_RESPONSE = {
    "code": 0,
    "msg": "OK",
    "request_id": "20260310001030D47244E85D621396E41C",
    "data": {
        "keyword_list": [
            {
                "comment": 436,
                "cost": 40700,
                "cpa": 0.03,
                "ctr": 4.15,
                "cvr": 100,
                "impression": 28300000,
                "keyword": "this game",
                "like": 30544,
                "play_six_rate": 18.79,
                "post": 23800,
                "post_change": 77.24,
                "share": 187,
                "video_list": [
                    "7571778224779267345",
                    "7589796090572967175",
                ],
            },
            {
                "comment": 399,
                "cost": 73200,
                "cpa": 0.01,
                "ctr": 11.1,
                "cvr": 100,
                "impression": 40200000,
                "keyword": "play now",
                "like": 53251,
                "play_six_rate": 24.42,
                "post": 20800,
                "post_change": 59.23,
                "share": 252,
                "video_list": [
                    "7611094939748896016",
                ],
            },
        ],
        "pagination": {
            "page": 1,
            "size": 20,
            "total": 500,
            "has_more": True,
        },
    },
}


def _build_job() -> TrendSearchJob:
    return TrendSearchJob(
        id=42,
        name="BY_7d_top10_live",
        countries=["Belarus"],
        time_window="7d",
        top_keywords_limit=10,
        related_videos_per_keyword=2,
        source_types=["tiktok_keyword_insights"],
        min_popularity_change=60.0,
    )


def test_build_request_params_from_job() -> None:
    source = TikTokKeywordInsightsSource(settings=AppSettings())
    params = source.build_request_params(_build_job(), "Belarus")

    assert params == {
        "page": 1,
        "limit": 10,
        "period": 7,
        "country_code": "BY",
        "order_by": "post",
        "order_type": "desc",
    }


def test_parse_keyword_trends_from_observed_response_shape() -> None:
    source = TikTokKeywordInsightsSource(settings=AppSettings())
    job = _build_job()

    items = source.parse_keyword_trends(SAMPLE_RESPONSE, job, "Belarus")

    assert len(items) == 1
    assert items[0].source == KEYWORD_SOURCE_NAME
    assert items[0].keyword == "this game"
    assert items[0].rank == 1
    assert items[0].popularity == 23800
    assert items[0].popularity_change == 77.24
    assert items[0].ctr == 4.15
    assert items[0].raw_payload_json["video_list"] == ["7571778224779267345", "7589796090572967175"]


def test_header_loading_from_app_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("T2V_TIKTOK_COOKIE_HEADER", "sessionid=abc")
    monkeypatch.setenv("T2V_TIKTOK_USER_AGENT", "codex-test-agent")
    monkeypatch.setenv(
        "T2V_TIKTOK_REFERER",
        "https://ads.tiktok.com/business/creativecenter/keyword-insights/pc/en",
    )
    monkeypatch.setenv("T2V_TIKTOK_ACCEPT_LANGUAGE", "en-US,en;q=0.9")
    monkeypatch.setenv(
        "T2V_TIKTOK_EXTRA_HEADERS_JSON",
        json.dumps({"X-CSRFToken": "token-123", "X-Test": 7}),
    )
    get_settings.cache_clear()  # type: ignore[attr-defined]
    settings = get_settings()
    source = TikTokKeywordInsightsSource(settings=settings)

    headers = source.build_headers()

    assert headers["cookie"] == "sessionid=abc"
    assert headers["user-agent"] == "codex-test-agent"
    assert headers["referer"] == "https://ads.tiktok.com/business/creativecenter/keyword-insights/pc/en"
    assert headers["accept-language"] == "en-US,en;q=0.9"
    assert headers["x-csrftoken"] == "token-123"
    assert headers["x-test"] == "7"
    get_settings.cache_clear()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_live_http_source_collects_keywords_and_related_videos_from_mocked_response() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        return httpx.Response(200, json=SAMPLE_RESPONSE, request=request)

    settings = AppSettings(
        tiktok_cookie_header="sessionid=abc",
        tiktok_user_agent="codex-test-agent",
        tiktok_referer="https://ads.tiktok.com/business/creativecenter/keyword-insights/pc/en",
        tiktok_accept_language="en-US,en;q=0.9",
    )
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        headers=TikTokKeywordInsightsSource(settings=settings).build_headers(),
    ) as client:
        source = TikTokKeywordInsightsSource(settings=settings, client=client)
        job = _build_job()

        keywords = await source.collect_keyword_trends(job)

        assert len(keywords) == 1
        assert KEYWORD_INSIGHTS_API_URL in str(captured["url"])
        assert "country_code=BY" in str(captured["url"])
        assert captured["headers"]["cookie"] == "sessionid=abc"

        keyword = keywords[0].model_copy(update={"id": 5})
        videos = await source.collect_related_videos(job, keyword)

        assert len(videos) == 2
        assert videos[0].source_url == "https://www.tiktok.com/video/7571778224779267345"
        assert videos[0].metadata_json["video_id"] == "7571778224779267345"


@pytest.mark.asyncio
async def test_collect_related_videos_reads_video_ids_from_keyword_payload() -> None:
    source = TikTokKeywordInsightsSource(settings=AppSettings())
    job = _build_job()
    keyword = KeywordTrend(
        id=9,
        job_id=42,
        source=KEYWORD_SOURCE_NAME,
        country="Belarus",
        time_window="7d",
        keyword="this game",
        raw_payload_json={"video_list": ["1", "2", "3"]},
    )

    videos = await source.collect_related_videos(job, keyword)

    assert [video.metadata_json["video_id"] for video in videos] == ["1", "2"]
