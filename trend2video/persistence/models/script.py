from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class ScriptORM(Base):
    __tablename__ = "scripts"
    """ORM-модель сгенерированного скрипта."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    trend_id: Mapped[int] = mapped_column(Integer, ForeignKey("trends.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[str] = mapped_column(String(255), ForeignKey("templates.id", ondelete="RESTRICT"), nullable=False)

    script_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'created'"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        server_onupdate=text("now()"),
    )

    __table_args__ = (
        UniqueConstraint("trend_id", name="uq_scripts_trend_id"),
    )

