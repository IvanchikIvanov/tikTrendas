from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, JSON, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.persistence.models.base import Base


class TemplateORM(Base):
    __tablename__ = "templates"

    """ORM-модель шаблона видео."""

    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    template_key: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)

    config_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

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
        UniqueConstraint("template_key", "version", name="uq_templates_key_version"),
    )
