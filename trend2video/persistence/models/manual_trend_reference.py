from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class ManualTrendReferenceORM(Base):
    __tablename__ = "manual_trend_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manual_trend_input_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("manual_trend_inputs.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_platform: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    hook_text: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
