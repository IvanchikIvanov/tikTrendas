from __future__ import annotations

import pytest
from pydantic import ValidationError

from trend2video.core.config import AppSettings
from trend2video.domain.entities.search_job import TrendSearchJob
from trend2video.integrations.tiktok.keyword_insights_source_static import StaticKeywordInsightsSource
from trend2video.integrations.tiktok.keyword_insights_source_tiktok import TikTokKeywordInsightsSource
from trend2video.integrations.tiktok.keyword_source_registry import build_keyword_insights_source_for_job


def test_search_job_validates_time_window() -> None:
    with pytest.raises(ValidationError):
        TrendSearchJob(
            name="bad",
            countries=["Belarus"],
            time_window="14d",
        )


def test_search_job_rejects_unknown_source_types() -> None:
    with pytest.raises(ValidationError):
        TrendSearchJob(
            name="bad-source",
            countries=["Belarus"],
            source_types=["tiktok_keyword_insights"],
        )


def test_search_job_defaults_source_types_to_empty_list() -> None:
    job = TrendSearchJob(
        name="default-source",
        countries=["Belarus"],
    )

    assert job.source_types == []


def test_build_keyword_source_uses_config_default_when_job_source_types_missing(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO")

    source = build_keyword_insights_source_for_job([], settings=AppSettings(default_keyword_source_type="static"))

    assert isinstance(source, StaticKeywordInsightsSource)
    assert "no source_types provided; using default keyword source" in caplog.text


def test_build_keyword_source_uses_canonical_live_key() -> None:
    source = build_keyword_insights_source_for_job(["tiktok_http"])

    assert isinstance(source, TikTokKeywordInsightsSource)
