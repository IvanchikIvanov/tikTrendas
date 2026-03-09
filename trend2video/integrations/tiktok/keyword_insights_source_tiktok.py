from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

import httpx

from trend2video.core.config import AppSettings, get_settings
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.entities.related_video import RelatedVideo
from trend2video.domain.entities.search_job import TrendSearchJob
from trend2video.integrations.tiktok.keyword_insights_source_base import KeywordInsightsSource


logger = logging.getLogger(__name__)

KEYWORD_INSIGHTS_API_URL = "https://ads.tiktok.com/creative_radar_api/v1/script/keyword/list"
KEYWORD_SOURCE_NAME = "tiktok_keyword_insights_http"
TIME_WINDOW_TO_PERIOD = {
    "1d": 1,
    "7d": 7,
    "30d": 30,
    "90d": 90,
}
COUNTRY_CODE_ALIASES = {
    "belarus": "BY",
    "brazil": "BR",
    "canada": "CA",
    "france": "FR",
    "germany": "DE",
    "india": "IN",
    "indonesia": "ID",
    "italy": "IT",
    "japan": "JP",
    "mexico": "MX",
    "philippines": "PH",
    "poland": "PL",
    "russia": "RU",
    "spain": "ES",
    "thailand": "TH",
    "turkey": "TR",
    "uk": "GB",
    "united kingdom": "GB",
    "united states": "US",
    "usa": "US",
    "vietnam": "VN",
}


class TikTokKeywordInsightsSource(KeywordInsightsSource):
    def __init__(
        self,
        settings: AppSettings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client = client

    async def collect_keyword_trends(self, job: TrendSearchJob) -> list[KeywordTrend]:
        async with self._get_client() as client:
            collected: list[KeywordTrend] = []
            for country in job.countries:
                params = self.build_request_params(job, country)
                response = await client.get(KEYWORD_INSIGHTS_API_URL, params=params)
                logger.info(
                    "keyword insights request completed",
                    extra={
                        "url": str(response.request.url),
                        "status_code": response.status_code,
                    },
                )

                payload = self._decode_payload(response)
                if payload is None:
                    continue

                code = payload.get("code")
                if code != 0:
                    logger.warning(
                        "keyword insights response returned non-zero code",
                        extra={"response_code": code, "country": country},
                    )
                    continue

                keywords = self.parse_keyword_trends(payload, job, country)
                logger.info(
                    "keyword insights parsed keywords",
                    extra={"country": country, "keyword_count": len(keywords)},
                )
                collected.extend(keywords)

            return collected

    async def collect_related_videos(
        self,
        job: TrendSearchJob,
        keyword_trend: KeywordTrend,
    ) -> list[RelatedVideo]:
        raw_video_ids = keyword_trend.raw_payload_json.get("video_list", [])
        if not isinstance(raw_video_ids, list):
            return []

        collected_at = datetime.now(timezone.utc)
        items: list[RelatedVideo] = []
        for index, raw_video_id in enumerate(raw_video_ids[: job.related_videos_per_keyword], start=1):
            if not raw_video_id:
                continue
            video_id = str(raw_video_id)
            items.append(
                RelatedVideo(
                    keyword_trend_id=keyword_trend.id or 0,
                    source_platform="tiktok",
                    source_url=f"https://www.tiktok.com/video/{video_id}",
                    metadata_json={
                        "video_id": video_id,
                        "video_list_position": index,
                        "source": KEYWORD_SOURCE_NAME,
                    },
                    collected_at=collected_at,
                )
            )
        return items

    def build_headers(self) -> dict[str, str]:
        headers = {
            "accept": "application/json, text/plain, */*",
        }
        optional_headers = {
            "cookie": self._settings.tiktok_cookie_header,
            "user-agent": self._settings.tiktok_user_agent,
            "referer": self._settings.tiktok_referer,
            "accept-language": self._settings.tiktok_accept_language,
        }
        headers.update({key: value for key, value in optional_headers.items() if value})
        headers.update(self._load_extra_headers())
        return headers

    def build_request_params(self, job: TrendSearchJob, country: str) -> dict[str, int | str]:
        return {
            "page": 1,
            "limit": job.top_keywords_limit,
            "period": TIME_WINDOW_TO_PERIOD[job.time_window],
            "country_code": self._resolve_country_code(country),
            "order_by": "post",
            "order_type": "desc",
        }

    def parse_keyword_trends(
        self,
        payload: Mapping[str, Any],
        job: TrendSearchJob,
        country: str,
    ) -> list[KeywordTrend]:
        rows = payload.get("data", {}).get("keyword_list", [])
        if not isinstance(rows, list):
            return []

        collected_at = datetime.now(timezone.utc)
        items: list[KeywordTrend] = []
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            popularity_change = self._as_float(row.get("post_change"))
            if popularity_change is not None and popularity_change < job.min_popularity_change:
                continue

            keyword = row.get("keyword")
            if not keyword:
                continue

            items.append(
                KeywordTrend(
                    job_id=job.id or 0,
                    source=KEYWORD_SOURCE_NAME,
                    country=country,
                    time_window=job.time_window,
                    keyword=str(keyword),
                    rank=index,
                    popularity=self._as_float(row.get("post")),
                    popularity_change=popularity_change,
                    ctr=self._as_float(row.get("ctr")),
                    collected_at=collected_at,
                    raw_payload_json=dict(row),
                )
            )
        return items

    def _decode_payload(self, response: httpx.Response) -> Mapping[str, Any] | None:
        try:
            payload = response.json()
        except json.JSONDecodeError:
            logger.warning(
                "keyword insights response json decode failed",
                extra={"body_preview": response.text[:500]},
            )
            return None
        if not isinstance(payload, dict):
            logger.warning("keyword insights response payload is not an object")
            return None
        return payload

    def _load_extra_headers(self) -> dict[str, str]:
        raw_value = self._settings.tiktok_extra_headers_json
        if not raw_value:
            return {}

        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValueError("T2V_TIKTOK_EXTRA_HEADERS_JSON must be valid JSON") from exc

        if not isinstance(parsed, dict):
            raise ValueError("T2V_TIKTOK_EXTRA_HEADERS_JSON must decode to a JSON object")

        headers: dict[str, str] = {}
        for key, value in parsed.items():
            if value is None:
                continue
            headers[str(key).lower()] = str(value)
        return headers

    def _resolve_country_code(self, country: str) -> str:
        normalized = country.strip()
        if len(normalized) == 2 and normalized.isalpha():
            return normalized.upper()

        alias_key = normalized.casefold()
        country_code = COUNTRY_CODE_ALIASES.get(alias_key)
        if country_code is None:
            raise ValueError(f"unsupported TikTok country value: {country}")
        return country_code

    def _get_client(self) -> httpx.AsyncClient | _AsyncClientContextAdapter:
        if self._client is not None:
            return _AsyncClientContextAdapter(self._client)
        return httpx.AsyncClient(headers=self.build_headers(), timeout=30.0)

    @staticmethod
    def _as_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


class _AsyncClientContextAdapter:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def __aenter__(self) -> httpx.AsyncClient:
        return self._client

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False
