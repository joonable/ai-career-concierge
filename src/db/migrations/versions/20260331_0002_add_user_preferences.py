"""Add user preferences column."""

import sqlalchemy as sa
from alembic import op

revision = "20260331_0002"
down_revision = "20260326_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("preferences", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.alter_column("users", "preferences", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "preferences")
