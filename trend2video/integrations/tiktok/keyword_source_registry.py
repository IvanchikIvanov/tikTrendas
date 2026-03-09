from __future__ import annotations

import logging
from collections.abc import Sequence

from trend2video.core.config import AppSettings, get_settings
from trend2video.integrations.tiktok.keyword_insights_source_base import KeywordInsightsSource
from trend2video.integrations.tiktok.keyword_insights_source_static import StaticKeywordInsightsSource
from trend2video.integrations.tiktok.keyword_insights_source_tiktok import TikTokKeywordInsightsSource
from trend2video.integrations.tiktok.keyword_source_types import (
    STATIC_SOURCE_TYPE,
    SUPPORTED_KEYWORD_SOURCE_TYPES,
    TIKTOK_HTTP_SOURCE_TYPE,
    normalize_source_types,
)


logger = logging.getLogger(__name__)


def build_keyword_insights_source_for_job(
    source_types: Sequence[str] | None,
    settings: AppSettings | None = None,
) -> KeywordInsightsSource:
    active_settings = settings or get_settings()
    normalized = normalize_source_types(source_types)
    if not normalized:
        logger.info(
            "no source_types provided; using default keyword source",
            extra={"default_keyword_source_type": active_settings.default_keyword_source_type},
        )
        return build_keyword_insights_source(active_settings.default_keyword_source_type, active_settings)
    return build_keyword_insights_source(normalized[0], active_settings)


def build_keyword_insights_source(
    source_type: str,
    settings: AppSettings | None = None,
) -> KeywordInsightsSource:
    active_settings = settings or get_settings()
    if source_type == TIKTOK_HTTP_SOURCE_TYPE:
        return TikTokKeywordInsightsSource(settings=active_settings)
    if source_type == STATIC_SOURCE_TYPE:
        return StaticKeywordInsightsSource(path=active_settings.static_keyword_insights_path)
    allowed = ", ".join(sorted(SUPPORTED_KEYWORD_SOURCE_TYPES))
    raise ValueError(f"unsupported keyword source type '{source_type}'. Allowed values: {allowed}")
