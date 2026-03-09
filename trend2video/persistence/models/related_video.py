from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class RelatedVideoORM(Base):
    __tablename__ = "related_videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword_trend_id: Mapped[int] = mapped_column(Integer, ForeignKey("keyword_trends.id", ondelete="CASCADE"), nullable=False)
    source_platform: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    creator_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    overlay_text: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    transcript: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    visual_tags_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    topic_tags_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("keyword_trend_id", "source_url", name="uq_related_videos_keyword_url"),
    )
