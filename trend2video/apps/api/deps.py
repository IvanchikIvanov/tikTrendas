from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from trend2video.core.config import AppSettings, get_settings
from trend2video.core.db import get_session
from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.services.asset_selector import AssetSelector
from trend2video.domain.services.candidate_builder import CandidateBuilder
from trend2video.domain.services.keyword_trend_scorer import KeywordTrendScorer
from trend2video.domain.services.manual_trend_candidate_builder import ManualTrendCandidateBuilder
from trend2video.domain.services.render_engine import RenderEngine
from trend2video.domain.services.render_manifest_builder import RenderManifestBuilder
from trend2video.domain.services.script_engine import ScriptEngine
from trend2video.domain.services.template_resolver import TemplateResolver
from trend2video.integrations.media.ffmpeg_runner import FFmpegRunner
from trend2video.integrations.llm.fake_llm import FakeLLMClient
from trend2video.integrations.tiktok.keyword_insights_source_base import KeywordInsightsSource
from trend2video.integrations.tiktok.keyword_source_registry import build_keyword_insights_source
from trend2video.persistence.repositories.asset_repository import AssetRepository
from trend2video.persistence.repositories.content_candidate_repository import ContentCandidateRepository
from trend2video.persistence.repositories.keyword_trend_repository import KeywordTrendRepository
from trend2video.persistence.repositories.manual_trend_repository import ManualTrendRepository
from trend2video.persistence.repositories.publish_job_repository import PublishJobRepository
from trend2video.persistence.repositories.related_video_repository import RelatedVideoRepository
from trend2video.persistence.repositories.render_job_repository import RenderJobRepository
from trend2video.persistence.repositories.review_request_repository import ReviewRequestRepository
from trend2video.persistence.repositories.script_repository import ScriptRepository
from trend2video.persistence.repositories.search_job_repository import SearchJobRepository
from trend2video.persistence.repositories.template_repository import TemplateRepository


async def get_settings_dep() -> AppSettings:
    return get_settings()


async def get_db_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_brand_context(settings: AppSettings = Depends(get_settings_dep)) -> BrandContext:
    return settings.brand_context


def get_search_job_repository(session: AsyncSession = Depends(get_db_session_dep)) -> SearchJobRepository:
    return SearchJobRepository(session)


def get_keyword_trend_repository(session: AsyncSession = Depends(get_db_session_dep)) -> KeywordTrendRepository:
    return KeywordTrendRepository(session)


def get_related_video_repository(session: AsyncSession = Depends(get_db_session_dep)) -> RelatedVideoRepository:
    return RelatedVideoRepository(session)


def get_content_candidate_repository(session: AsyncSession = Depends(get_db_session_dep)) -> ContentCandidateRepository:
    return ContentCandidateRepository(session)


def get_template_repository(session: AsyncSession = Depends(get_db_session_dep)) -> TemplateRepository:
    return TemplateRepository(session)


def get_script_repository(session: AsyncSession = Depends(get_db_session_dep)) -> ScriptRepository:
    return ScriptRepository(session)


def get_manual_trend_repository(session: AsyncSession = Depends(get_db_session_dep)) -> ManualTrendRepository:
    return ManualTrendRepository(session)


def get_asset_repository(session: AsyncSession = Depends(get_db_session_dep)) -> AssetRepository:
    return AssetRepository(session)


def get_render_job_repository(session: AsyncSession = Depends(get_db_session_dep)) -> RenderJobRepository:
    return RenderJobRepository(session)


def get_review_request_repository(session: AsyncSession = Depends(get_db_session_dep)) -> ReviewRequestRepository:
    return ReviewRequestRepository(session)


def get_publish_job_repository(session: AsyncSession = Depends(get_db_session_dep)) -> PublishJobRepository:
    return PublishJobRepository(session)


def get_keyword_trend_scorer() -> KeywordTrendScorer:
    return KeywordTrendScorer()


def get_candidate_builder(
    scorer: KeywordTrendScorer = Depends(get_keyword_trend_scorer),
) -> CandidateBuilder:
    return CandidateBuilder(scorer)


def get_template_resolver() -> TemplateResolver:
    return TemplateResolver()


def get_manual_trend_candidate_builder() -> ManualTrendCandidateBuilder:
    return ManualTrendCandidateBuilder()


def get_asset_selector() -> AssetSelector:
    return AssetSelector()


def get_render_manifest_builder(
    selector: AssetSelector = Depends(get_asset_selector),
) -> RenderManifestBuilder:
    return RenderManifestBuilder(selector)


def get_ffmpeg_runner() -> FFmpegRunner:
    return FFmpegRunner()


def get_render_engine(runner: FFmpegRunner = Depends(get_ffmpeg_runner)) -> RenderEngine:
    return RenderEngine(runner)


def get_llm_client(brand_ctx: BrandContext = Depends(get_brand_context)) -> FakeLLMClient:
    return FakeLLMClient(brand_ctx)


def get_script_engine(llm_client: FakeLLMClient = Depends(get_llm_client)) -> ScriptEngine:
    return ScriptEngine(llm_client)


def get_keyword_insights_source(
    settings: AppSettings = Depends(get_settings_dep),
) -> KeywordInsightsSource:
    return build_keyword_insights_source(settings.default_keyword_source_type, settings)
