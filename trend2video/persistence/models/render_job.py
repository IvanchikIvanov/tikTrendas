from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class RenderJobORM(Base):
    __tablename__ = "render_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content_candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_candidates.id", ondelete="CASCADE"), nullable=False)
    script_id: Mapped[int] = mapped_column(Integer, ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[str] = mapped_column(String(255), ForeignKey("templates.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'pending'"))
    render_manifest_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    output_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    preview_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    error: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
