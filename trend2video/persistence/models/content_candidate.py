from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class ContentCandidateORM(Base):
    __tablename__ = "content_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("trend_search_jobs.id", ondelete="CASCADE"), nullable=False)
    keyword_trend_id: Mapped[int] = mapped_column(Integer, ForeignKey("keyword_trends.id", ondelete="CASCADE"), nullable=False)
    candidate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    signal_score: Mapped[float] = mapped_column(Float, nullable=False)
    product_relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    scriptability_score: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_angle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, server_default=text("'candidate'"))
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        Index("ix_content_candidates_job_id", "job_id"),
        Index("ix_content_candidates_job_score", "job_id", "scriptability_score", "signal_score"),
        Index("ix_content_candidates_keyword_trend_id", "keyword_trend_id"),
    )
