from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from trend2video.domain.entities.brand import BrandContext


class AppSettings(BaseSettings):
    """Глобальные настройки приложения."""

    model_config = SettingsConfigDict(env_prefix="T2V_", env_file=".env", extra="ignore")

    env: str = "local"

    # БД
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/trend2video"

    # Источники трендов
    trend_source: Literal["creative_center", "static"] = "static"
    static_trends_path: str = "data/static_trends.json"
    default_keyword_source_type: Literal["static", "tiktok_keyword_insights"] = "static"
    static_keyword_insights_path: str = "data/static_keyword_insights.json"
    default_related_videos_per_keyword: int = 3
    default_top_keywords_limit: int = 10

    # TikTok Creative Center
    tiktok_creative_center_url: str = "https://www.tiktok.com/business/creativecenter/inspiration/popular/hashtag"
    tiktok_region: str = "US"
    tiktok_cookie_header: str | None = None
    tiktok_user_agent: str | None = None
    tiktok_referer: str | None = None
    tiktok_accept_language: str | None = None
    tiktok_extra_headers_json: str | None = None
    tiktok_storage_state_path: str | None = None
    media_storage_base_path: str = "data/media"

    # Brand context
    brand_context: BrandContext = Field(
        default_factory=lambda: BrandContext(
            product_name="LeadFlow",
            product_type="sales automation platform",
            audience=["small business owners", "sales teams", "marketers"],
            pain_points=[
                "slow lead response",
                "manual qualification",
                "lost inbound requests",
            ],
            tone="direct",
            forbidden_topics=["medical claims", "fake guarantees"],
            cta_style="short_direct",
            niche_tags=["sales", "automation", "leadgen"],
        )
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Кэшированный доступ к настройкам приложения."""

    return AppSettings()
