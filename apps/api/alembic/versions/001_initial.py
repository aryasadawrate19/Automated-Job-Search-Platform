"""Initial schema — jobs, users, matches with pgvector.

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-29
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create experience_level enum
    experience_level_enum = sa.Enum(
        "junior", "mid", "senior", "lead", name="experience_level_enum"
    )

    # Create remote_preference enum
    remote_preference_enum = sa.Enum(
        "only", "preferred", "open", name="remote_preference_enum"
    )

    # Create ai_provider enum
    ai_provider_enum = sa.Enum("anthropic", "gemini", "openai", name="ai_provider_enum")

    # ── Jobs table ─────────────────────────────────────────────────────
    op.create_table(
        "jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False, index=True),
        sa.Column("source_url", sa.String(2048), unique=True, nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("company", sa.String(300), nullable=False),
        sa.Column("location", sa.String(300), nullable=True),
        sa.Column("remote", sa.Boolean, default=False),
        sa.Column("description_raw", sa.Text, nullable=True),
        sa.Column("description_normalized", sa.Text, nullable=True),
        sa.Column("skills_extracted", JSONB, server_default="[]"),
        sa.Column(
            "experience_level",
            experience_level_enum,
            nullable=True,
        ),
        sa.Column("salary_min", sa.Integer, nullable=True),
        sa.Column("salary_max", sa.Integer, nullable=True),
        sa.Column("posted_at", sa.DateTime, nullable=True),
        sa.Column("ingested_at", sa.DateTime, server_default=sa.func.now()),
    )
    # pgvector column for job embeddings
    op.execute("ALTER TABLE jobs ADD COLUMN embedding vector(384)")

    # ── Users table ────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), unique=True, nullable=False, index=True),
        sa.Column("resume_raw", sa.Text, nullable=True),
        sa.Column("skills", JSONB, server_default="[]"),
        sa.Column("experience_years", sa.Float, default=0.0),
        sa.Column(
            "experience_level",
            experience_level_enum,
            server_default="junior",
        ),
        sa.Column("preferred_roles", JSONB, server_default="[]"),
        sa.Column("preferred_locations", JSONB, server_default="[]"),
        sa.Column(
            "remote_preference",
            remote_preference_enum,
            server_default="open",
        ),
        # Encrypted AI provider keys
        sa.Column("anthropic_api_key_enc", sa.LargeBinary, nullable=True),
        sa.Column("gemini_api_key_enc", sa.LargeBinary, nullable=True),
        sa.Column("openai_api_key_enc", sa.LargeBinary, nullable=True),
        sa.Column(
            "ai_provider",
            ai_provider_enum,
            server_default="anthropic",
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    # pgvector column for profile embeddings
    op.execute("ALTER TABLE users ADD COLUMN profile_embedding vector(384)")

    # ── Matches table ──────────────────────────────────────────────────
    op.create_table(
        "matches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rule_score", sa.Float, default=0.0),
        sa.Column("semantic_score", sa.Float, default=0.0),
        sa.Column("final_score", sa.Float, default=0.0, index=True),
        sa.Column("matched_skills", JSONB, server_default="[]"),
        sa.Column("missing_skills", JSONB, server_default="[]"),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("computed_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "job_id", name="uq_user_job"),
    )

    # ── Indexes ────────────────────────────────────────────────────────
    # IVFFlat index for ANN search on job embeddings
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_jobs_embedding "
        "ON jobs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_users_embedding "
        "ON users USING ivfflat (profile_embedding vector_cosine_ops) WITH (lists = 50)"
    )


def downgrade() -> None:
    op.drop_table("matches")
    op.drop_table("users")
    op.drop_table("jobs")
    op.execute("DROP TYPE IF EXISTS experience_level_enum")
    op.execute("DROP TYPE IF EXISTS remote_preference_enum")
    op.execute("DROP TYPE IF EXISTS ai_provider_enum")
    op.execute("DROP EXTENSION IF EXISTS vector")
