"""Add v2 trend discovery schema and migrate scripts relations."""

from __future__ import annotations

from typing import Sequence, Union

from alembic import context, op  # type: ignore[import]
import sqlalchemy as sa  # type: ignore[import]


revision: str = "0002_trend_discovery_v2_schema"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _assert_scripts_table_empty(bind: sa.Connection, reason: str) -> None:
    if context.is_offline_mode():
        return
    script_count = bind.execute(sa.text("SELECT COUNT(*) FROM scripts")).scalar_one()
    if script_count:
        raise RuntimeError(
            f"Cannot {reason} while scripts contains {script_count} row(s). "
            "Backfill or remove legacy script rows first."
        )


def upgrade() -> None:
    op.create_table(
        "trend_search_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("countries_json", sa.JSON(), nullable=False),
        sa.Column("time_window", sa.String(length=32), nullable=False),
        sa.Column("top_keywords_limit", sa.Integer(), nullable=False),
        sa.Column("related_videos_per_keyword", sa.Integer(), nullable=False),
        sa.Column("source_types_json", sa.JSON(), nullable=False),
        sa.Column("min_popularity_change", sa.Float(), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=True),
        sa.Column("product_tags_json", sa.JSON(), nullable=False),
        sa.Column("mode", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("name", name="uq_trend_search_jobs_name"),
    )
    op.create_index("ix_trend_search_jobs_is_active", "trend_search_jobs", ["is_active"], unique=False)

    op.create_table(
        "keyword_trends",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("country", sa.String(length=128), nullable=False),
        sa.Column("time_window", sa.String(length=32), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("popularity", sa.Float(), nullable=True),
        sa.Column("popularity_change", sa.Float(), nullable=True),
        sa.Column("ctr", sa.Float(), nullable=True),
        sa.Column("keyword_type", sa.String(length=64), nullable=True),
        sa.Column("industry", sa.String(length=128), nullable=True),
        sa.Column("objective", sa.String(length=128), nullable=True),
        sa.Column("details_url", sa.String(length=512), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["job_id"], ["trend_search_jobs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("job_id", "country", "time_window", "keyword", name="uq_keyword_trends_job_scope"),
    )
    op.create_index("ix_keyword_trends_job_id", "keyword_trends", ["job_id"], unique=False)
    op.create_index(
        "ix_keyword_trends_job_rank",
        "keyword_trends",
        ["job_id", "popularity_change", "rank"],
        unique=False,
    )

    op.create_table(
        "related_videos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("keyword_trend_id", sa.Integer(), nullable=False),
        sa.Column("source_platform", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=False),
        sa.Column("creator_name", sa.String(length=255), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=1024), nullable=True),
        sa.Column("storage_path", sa.String(length=1024), nullable=True),
        sa.Column("overlay_text", sa.String(length=1024), nullable=True),
        sa.Column("transcript", sa.String(length=5000), nullable=True),
        sa.Column("duration_sec", sa.Float(), nullable=True),
        sa.Column("visual_tags_json", sa.JSON(), nullable=False),
        sa.Column("topic_tags_json", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["keyword_trend_id"], ["keyword_trends.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("keyword_trend_id", "source_url", name="uq_related_videos_keyword_url"),
    )
    op.create_index("ix_related_videos_keyword_trend_id", "related_videos", ["keyword_trend_id"], unique=False)

    op.create_table(
        "content_candidates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("keyword_trend_id", sa.Integer(), nullable=False),
        sa.Column("candidate_type", sa.String(length=64), nullable=False),
        sa.Column("signal_score", sa.Float(), nullable=False),
        sa.Column("product_relevance_score", sa.Float(), nullable=False),
        sa.Column("scriptability_score", sa.Float(), nullable=False),
        sa.Column("recommended_angle", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False, server_default=sa.text("'candidate'")),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["job_id"], ["trend_search_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["keyword_trend_id"], ["keyword_trends.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_content_candidates_job_id", "content_candidates", ["job_id"], unique=False)
    op.create_index(
        "ix_content_candidates_job_score",
        "content_candidates",
        ["job_id", "scriptability_score", "signal_score"],
        unique=False,
    )
    op.create_index("ix_content_candidates_keyword_trend_id", "content_candidates", ["keyword_trend_id"], unique=False)

    bind = op.get_bind()
    _assert_scripts_table_empty(bind, "upgrade scripts to the v2 schema")

    with op.batch_alter_table("scripts") as batch_op:
        batch_op.drop_constraint("uq_scripts_trend_id", type_="unique")
        batch_op.add_column(sa.Column("content_candidate_id", sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column("keyword_trend_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_scripts_content_candidate_id_content_candidates",
            "content_candidates",
            ["content_candidate_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_foreign_key(
            "fk_scripts_keyword_trend_id_keyword_trends",
            "keyword_trends",
            ["keyword_trend_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_unique_constraint("uq_scripts_content_candidate_id", ["content_candidate_id"])
        batch_op.drop_column("trend_id")

    op.create_index("ix_scripts_keyword_trend_id", "scripts", ["keyword_trend_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    _assert_scripts_table_empty(bind, "downgrade scripts back to the v1 schema")

    op.drop_index("ix_scripts_keyword_trend_id", table_name="scripts")

    with op.batch_alter_table("scripts") as batch_op:
        batch_op.drop_constraint("uq_scripts_content_candidate_id", type_="unique")
        batch_op.drop_constraint("fk_scripts_content_candidate_id_content_candidates", type_="foreignkey")
        batch_op.drop_constraint("fk_scripts_keyword_trend_id_keyword_trends", type_="foreignkey")
        batch_op.add_column(sa.Column("trend_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, "trends", ["trend_id"], ["id"], ondelete="CASCADE")
        batch_op.create_unique_constraint("uq_scripts_trend_id", ["trend_id"])
        batch_op.drop_column("keyword_trend_id")
        batch_op.drop_column("content_candidate_id")

    op.drop_index("ix_content_candidates_keyword_trend_id", table_name="content_candidates")
    op.drop_index("ix_content_candidates_job_score", table_name="content_candidates")
    op.drop_index("ix_content_candidates_job_id", table_name="content_candidates")
    op.drop_table("content_candidates")

    op.drop_index("ix_related_videos_keyword_trend_id", table_name="related_videos")
    op.drop_table("related_videos")

    op.drop_index("ix_keyword_trends_job_rank", table_name="keyword_trends")
    op.drop_index("ix_keyword_trends_job_id", table_name="keyword_trends")
    op.drop_table("keyword_trends")

    op.drop_index("ix_trend_search_jobs_is_active", table_name="trend_search_jobs")
    op.drop_table("trend_search_jobs")
