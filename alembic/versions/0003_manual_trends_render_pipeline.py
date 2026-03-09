"""Add manual trend, render, review, publish, and asset schema."""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op  # type: ignore[import]
import sqlalchemy as sa  # type: ignore[import]


revision: str = "0003_manual_trends_render_pipeline"
down_revision: Union[str, None] = "0002_trend_discovery_v2_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "manual_trend_inputs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("trend_type", sa.String(length=64), nullable=False),
        sa.Column("country", sa.String(length=128), nullable=False),
        sa.Column("time_window", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.String(length=4000), nullable=True),
        sa.Column("reference_hook_texts_json", sa.JSON(), nullable=False),
        sa.Column("related_video_urls_json", sa.JSON(), nullable=False),
        sa.Column("manual_tags_json", sa.JSON(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("status", sa.String(length=64), nullable=False, server_default=sa.text("'new'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "manual_trend_references",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("manual_trend_input_id", sa.Integer(), nullable=False),
        sa.Column("source_platform", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=False),
        sa.Column("hook_text", sa.String(length=1024), nullable=True),
        sa.Column("notes", sa.String(length=4000), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["manual_trend_input_id"], ["manual_trend_inputs.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asset_type", sa.String(length=64), nullable=False),
        sa.Column("asset_tag", sa.String(length=128), nullable=False),
        sa.Column("path", sa.String(length=1024), nullable=False),
        sa.Column("duration_sec", sa.Float(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    with op.batch_alter_table("content_candidates") as batch_op:
        batch_op.alter_column("job_id", existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column("keyword_trend_id", existing_type=sa.Integer(), nullable=True)
        batch_op.add_column(sa.Column("manual_trend_input_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("source_type", sa.String(length=32), nullable=False, server_default=sa.text("'keyword_trend'")))
        batch_op.create_foreign_key(
            "fk_content_candidates_manual_trend_input_id_manual_trend_inputs",
            "manual_trend_inputs",
            ["manual_trend_input_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.create_index("ix_content_candidates_manual_trend_input_id", "content_candidates", ["manual_trend_input_id"], unique=False)

    op.create_table(
        "render_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("content_candidate_id", sa.Integer(), nullable=False),
        sa.Column("script_id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("render_manifest_json", sa.JSON(), nullable=False),
        sa.Column("output_path", sa.String(length=1024), nullable=True),
        sa.Column("preview_path", sa.String(length=1024), nullable=True),
        sa.Column("error", sa.String(length=4000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["content_candidate_id"], ["content_candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"], ondelete="RESTRICT"),
    )

    op.create_table(
        "review_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("render_job_id", sa.Integer(), nullable=False),
        sa.Column("channel_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("reviewer", sa.String(length=255), nullable=True),
        sa.Column("review_comment", sa.String(length=4000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["render_job_id"], ["render_jobs.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "publish_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("render_job_id", sa.Integer(), nullable=False),
        sa.Column("target_platform", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["render_job_id"], ["render_jobs.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("publish_jobs")
    op.drop_table("review_requests")
    op.drop_table("render_jobs")
    op.drop_index("ix_content_candidates_manual_trend_input_id", table_name="content_candidates")

    with op.batch_alter_table("content_candidates") as batch_op:
        batch_op.drop_constraint("fk_content_candidates_manual_trend_input_id_manual_trend_inputs", type_="foreignkey")
        batch_op.drop_column("source_type")
        batch_op.drop_column("manual_trend_input_id")
        batch_op.alter_column("keyword_trend_id", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("job_id", existing_type=sa.Integer(), nullable=False)

    op.drop_table("assets")
    op.drop_table("manual_trend_references")
    op.drop_table("manual_trend_inputs")
