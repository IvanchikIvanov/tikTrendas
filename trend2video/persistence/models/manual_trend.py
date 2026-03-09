from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class ManualTrendInputORM(Base):
    __tablename__ = "manual_trend_inputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    trend_type: Mapped[str] = mapped_column(String(64), nullable=False)
    country: Mapped[str] = mapped_column(String(128), nullable=False)
    time_window: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    reference_hook_texts_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    related_video_urls_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    manual_tags_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    status: Mapped[str] = mapped_column(String(64), nullable=False, server_default=text("'new'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
