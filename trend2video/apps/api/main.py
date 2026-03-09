from __future__ import annotations

from fastapi import FastAPI

from trend2video.apps.api.routes import candidates, health, keyword_trends, related_videos, scripts, search_jobs
from trend2video.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="trend2video", version="0.2.0")
    app.include_router(health.router)
    app.include_router(search_jobs.router)
    app.include_router(keyword_trends.router)
    app.include_router(related_videos.router)
    app.include_router(candidates.router)
    app.include_router(scripts.router)
    return app


app = create_app()
