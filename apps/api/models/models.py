"""SQLAlchemy ORM models — jobs, users, matches with pgvector support."""

import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from apps.api.core.database import Base


# ── Enums ──────────────────────────────────────────────────────────────


class ExperienceLevel(str, enum.Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"


class RemotePreference(str, enum.Enum):
    only = "only"
    preferred = "preferred"
    open = "open"


class AIProvider(str, enum.Enum):
    anthropic = "anthropic"
    gemini = "gemini"
    openai = "openai"


# ── Jobs ───────────────────────────────────────────────────────────────


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False, index=True)
    source_url = Column(String(2048), unique=True, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    company = Column(String(300), nullable=False)
    location = Column(String(300), nullable=True)
    remote = Column(Boolean, default=False)
    description_raw = Column(Text, nullable=True)
    description_normalized = Column(Text, nullable=True)
    skills_extracted = Column(JSONB, default=list)
    experience_level = Column(
        Enum(ExperienceLevel, name="experience_level_enum"),
        nullable=True,
    )
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(Vector(384), nullable=True)

    # Relationships
    matches = relationship("Match", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job {self.title} @ {self.company}>"


# ── Users ──────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), unique=True, nullable=False, index=True)
    resume_raw = Column(Text, nullable=True)
    skills = Column(JSONB, default=list)
    experience_years = Column(Float, default=0.0)
    experience_level = Column(
        Enum(ExperienceLevel, name="experience_level_enum", create_type=False),
        default=ExperienceLevel.junior,
    )
    preferred_roles = Column(JSONB, default=list)
    preferred_locations = Column(JSONB, default=list)
    remote_preference = Column(
        Enum(RemotePreference, name="remote_preference_enum"),
        default=RemotePreference.open,
    )
    profile_embedding = Column(Vector(384), nullable=True)

    # Encrypted AI provider keys
    anthropic_api_key_enc = Column(LargeBinary, nullable=True)
    gemini_api_key_enc = Column(LargeBinary, nullable=True)
    openai_api_key_enc = Column(LargeBinary, nullable=True)
    ai_provider = Column(
        Enum(AIProvider, name="ai_provider_enum"),
        default=AIProvider.anthropic,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matches = relationship("Match", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


# ── Matches ────────────────────────────────────────────────────────────


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    job_id = Column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    rule_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0, index=True)
    matched_skills = Column(JSONB, default=list)
    missing_skills = Column(JSONB, default=list)
    explanation = Column(Text, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="matches")
    job = relationship("Job", back_populates="matches")

    def __repr__(self):
        return f"<Match user={self.user_id} job={self.job_id} score={self.final_score:.2f}>"
