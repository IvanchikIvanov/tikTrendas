from __future__ import annotations

from fastapi import FastAPI

from trend2video.apps.api.routes import health, trends, scripts
from trend2video.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="trend2video", version="0.1.0")
    app.include_router(health.router)
    app.include_router(trends.router)
    app.include_router(scripts.router)
    return app


app = create_app()

