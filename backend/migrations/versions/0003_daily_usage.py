"""Preserve anonymous provider totals independently of account deletion."""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("daily_usage", sa.Column("day", sa.Date(), primary_key=True),
                    sa.Column("attempts", sa.Integer(), nullable=False))
    op.execute(sa.text("INSERT INTO daily_usage(day, attempts) SELECT DATE(created_at), COUNT(*) FROM analysis_attempts GROUP BY DATE(created_at)"))


def downgrade():
    op.drop_table("daily_usage")
