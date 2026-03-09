from __future__ import annotations

from fastapi import FastAPI

from trend2video.apps.api.routes import (
    assets,
    candidates,
    health,
    keyword_trends,
    manual_trends,
    publish_jobs,
    related_videos,
    renders,
    review_requests,
    scripts,
    search_jobs,
)
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
    app.include_router(manual_trends.router)
    app.include_router(assets.router)
    app.include_router(renders.router)
    app.include_router(review_requests.router)
    app.include_router(publish_jobs.router)
    return app


app = create_app()
