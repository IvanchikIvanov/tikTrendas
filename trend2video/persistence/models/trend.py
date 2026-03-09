from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer, JSON, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from trend2video.domain.entities.trend import TrendStatus
from trend2video.persistence.models.base import Base


class TrendORM(Base):
    __tablename__ = "trends"

    """ORM-модель тренда в БД."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    trend_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    region: Mapped[str] = mapped_column(String(32), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)

    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heat: Mapped[float | None] = mapped_column(Float, nullable=True)
    velocity: Mapped[float | None] = mapped_column(Float, nullable=True)

    tags_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    raw_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[TrendStatus] = mapped_column(
        Enum(
            TrendStatus,
            name="trend_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
        server_default=TrendStatus.DISCOVERED.value,
    )

    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
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
        UniqueConstraint("source", "external_id", name="uq_trends_source_external_id"),
    )
