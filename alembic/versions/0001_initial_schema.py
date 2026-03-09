"""Initial schema: trends, templates, scripts."""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op  # type: ignore[import]
import sqlalchemy as sa  # type: ignore[import]
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trends",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("trend_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("region", sa.String(length=32), nullable=False),
        sa.Column("industry", sa.String(length=128), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("heat", sa.Float(), nullable=True),
        sa.Column("velocity", sa.Float(), nullable=True),
        sa.Column("tags_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("raw_payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("discovered", "scored", "template_selected", "script_generated", "skipped", "failed", name="trend_status"),
            nullable=False,
            server_default="discovered",
        ),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("source", "external_id", name="uq_trends_source_external_id"),
    )

    op.create_table(
        "templates",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column("template_key", sa.String(length=128), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("template_key", "version", name="uq_templates_key_version"),
    )

    op.create_table(
        "scripts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("trend_id", sa.Integer(), sa.ForeignKey("trends.id", ondelete="CASCADE"), nullable=False),
        sa.Column("template_id", sa.String(length=255), sa.ForeignKey("templates.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("script_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="created"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("trend_id", name="uq_scripts_trend_id"),
    )


def downgrade() -> None:
    op.drop_table("scripts")
    op.drop_table("templates")
    op.drop_table("trends")
    op.execute("DROP TYPE IF EXISTS trend_status")

