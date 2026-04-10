"""Initial schema."""

import sqlalchemy as sa
from alembic import op

revision = "20260326_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("oauth_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("profile_data", sa.JSON(), nullable=False),
        sa.Column("guidelines", sa.JSON(), nullable=False),
        sa.Column("notification_settings", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("oauth_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_oauth_id"), "users", ["oauth_id"], unique=False)

    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=100), nullable=False),
        sa.Column("external_job_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("jd_raw_text", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("min_years_experience", sa.Integer(), nullable=True),
        sa.Column("max_years_experience", sa.Integer(), nullable=True),
        sa.Column("source_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "external_job_id", name="uq_jobs_platform_external"),
    )
    op.create_index(op.f("ix_jobs_external_job_id"), "jobs", ["external_job_id"], unique=False)
    op.create_index(op.f("ix_jobs_platform"), "jobs", ["platform"], unique=False)

    op.create_table(
        "evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("fit_score", sa.Integer(), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("rule_rejection_reason", sa.String(length=255), nullable=True),
        sa.Column("user_feedback", sa.String(length=16), nullable=True),
        sa.Column("feedback_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_evaluations_user_job"),
    )
    op.create_index(op.f("ix_evaluations_job_id"), "evaluations", ["job_id"], unique=False)
    op.create_index(op.f("ix_evaluations_user_id"), "evaluations", ["user_id"], unique=False)

    op.create_table(
        "system_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("job_id", sa.Uuid(), nullable=True),
        sa.Column("platform", sa.String(length=100), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_system_logs_event_type"), "system_logs", ["event_type"], unique=False)
    op.create_index(op.f("ix_system_logs_job_id"), "system_logs", ["job_id"], unique=False)
    op.create_index(op.f("ix_system_logs_run_id"), "system_logs", ["run_id"], unique=False)
    op.create_index(op.f("ix_system_logs_user_id"), "system_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_system_logs_user_id"), table_name="system_logs")
    op.drop_index(op.f("ix_system_logs_run_id"), table_name="system_logs")
    op.drop_index(op.f("ix_system_logs_job_id"), table_name="system_logs")
    op.drop_index(op.f("ix_system_logs_event_type"), table_name="system_logs")
    op.drop_table("system_logs")

    op.drop_index(op.f("ix_evaluations_user_id"), table_name="evaluations")
    op.drop_index(op.f("ix_evaluations_job_id"), table_name="evaluations")
    op.drop_table("evaluations")

    op.drop_index(op.f("ix_jobs_platform"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_external_job_id"), table_name="jobs")
    op.drop_table("jobs")

    op.drop_index(op.f("ix_users_oauth_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
