"""Generic Alembic revision script."""

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

from alembic import op  # type: ignore[import]
import sqlalchemy as sa  # type: ignore[import]


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

