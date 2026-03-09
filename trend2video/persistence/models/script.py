from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class ScriptORM(Base):
    __tablename__ = "scripts"
    """ORM-модель сгенерированного скрипта."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    content_candidate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("content_candidates.id", ondelete="CASCADE"),
        nullable=False,
    )
    keyword_trend_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("keyword_trends.id", ondelete="SET NULL"),
        nullable=True,
    )
    template_id: Mapped[str] = mapped_column(String(255), ForeignKey("templates.id", ondelete="RESTRICT"), nullable=False)

    script_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'created'"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    __table_args__ = (
        UniqueConstraint("content_candidate_id", name="uq_scripts_content_candidate_id"),
        Index("ix_scripts_keyword_trend_id", "keyword_trend_id"),
    )
