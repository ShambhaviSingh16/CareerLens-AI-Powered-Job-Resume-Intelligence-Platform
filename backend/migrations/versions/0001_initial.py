"""Initial users, resumes, jobs and analyses schema."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("email", sa.String(255), nullable=False),
                    sa.Column("password_hash", sa.String(255), nullable=False),
                    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("resumes", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
                    sa.Column("filename", sa.String(255), nullable=False),
                    sa.Column("extracted_text", sa.Text(), nullable=False),
                    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])
    op.create_table("jobs", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
                    sa.Column("title", sa.String(255), nullable=False),
                    sa.Column("company", sa.String(255), nullable=True),
                    sa.Column("description", sa.Text(), nullable=False),
                    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])
    op.create_table("analyses", sa.Column("id", sa.Integer(), primary_key=True),
                    sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
                    sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id"), nullable=False),
                    sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
                    sa.Column("match_score", sa.Integer(), nullable=True),
                    sa.Column("result", sa.JSON().with_variant(JSONB, "postgresql"), nullable=True),
                    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    for name in ("user_id", "resume_id", "job_id"):
        op.create_index(f"ix_analyses_{name}", "analyses", [name])


def downgrade():
    for table in ("analyses", "jobs", "resumes", "users"):
        op.drop_table(table)
