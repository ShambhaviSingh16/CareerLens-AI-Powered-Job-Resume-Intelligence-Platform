"""Persist provider-attempt quota independently of deletable results."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("analysis_attempts",
                    sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
                    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_analysis_attempts_user_id", "analysis_attempts", ["user_id"])


def downgrade():
    op.drop_table("analysis_attempts")
