from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class TrendSearchJobORM(Base):
    __tablename__ = "trend_search_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    countries_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    time_window: Mapped[str] = mapped_column(String(32), nullable=False)
    top_keywords_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    related_videos_per_keyword: Mapped[int] = mapped_column(Integer, nullable=False)
    source_types_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    min_popularity_change: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    product_tags_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    mode: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
