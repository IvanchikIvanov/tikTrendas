from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.core.config import AppSettings, get_settings
from trend2video.core.db import get_session
from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.services.script_engine import ScriptEngine
from trend2video.domain.services.template_resolver import TemplateResolver
from trend2video.domain.services.trend_scorer import TrendScorer
from trend2video.domain.services.trend_normalizer import TrendNormalizer
from trend2video.integrations.llm.fake_llm import FakeLLMClient
from trend2video.integrations.tiktok.trend_source_base import TrendSource
from trend2video.integrations.tiktok.trend_source_creative_center import CreativeCenterTrendSource
from trend2video.integrations.tiktok.trend_source_static import StaticJsonTrendSource
from trend2video.persistence.repositories.script_repository import ScriptRepository
from trend2video.persistence.repositories.template_repository import TemplateRepository
from trend2video.persistence.repositories.trend_repository import TrendRepository


async def get_settings_dep() -> AppSettings:
    return get_settings()


async def get_db_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async for s in get_session():
        yield s


def get_brand_context(settings: AppSettings = Depends(get_settings_dep)) -> BrandContext:
    return settings.brand_context


def get_trend_repository(
    session: AsyncSession = Depends(get_db_session_dep),
) -> TrendRepository:
    return TrendRepository(session)


def get_template_repository(
    session: AsyncSession = Depends(get_db_session_dep),
) -> TemplateRepository:
    return TemplateRepository(session)


def get_script_repository(
    session: AsyncSession = Depends(get_db_session_dep),
) -> ScriptRepository:
    return ScriptRepository(session)


def get_trend_scorer() -> TrendScorer:
    return TrendScorer()


def get_template_resolver() -> TemplateResolver:
    return TemplateResolver()


def get_llm_client(
    brand_ctx: BrandContext = Depends(get_brand_context),
) -> FakeLLMClient:
    # Для Sprint 1 используем только FakeLLMClient.
    return FakeLLMClient(brand_ctx)


def get_script_engine(llm_client: FakeLLMClient = Depends(get_llm_client)) -> ScriptEngine:
    return ScriptEngine(llm_client)


def get_trend_source(
    settings: AppSettings = Depends(get_settings_dep),
) -> TrendSource:
    normalizer = TrendNormalizer()
    if settings.trend_source == "creative_center":
        return CreativeCenterTrendSource(normalizer=normalizer)
    return StaticJsonTrendSource(normalizer=normalizer, path=settings.static_trends_path)

