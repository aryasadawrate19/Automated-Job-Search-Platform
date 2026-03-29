"""Pydantic v2 schemas for API request/response validation."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────────


class ExperienceLevel(str, Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"


class RemotePreference(str, Enum):
    only = "only"
    preferred = "preferred"
    open = "open"


class AIProvider(str, Enum):
    anthropic = "anthropic"
    gemini = "gemini"
    openai = "openai"


# ── User Schemas ───────────────────────────────────────────────────────


class UserRegister(BaseModel):
    email: str = Field(..., max_length=320)


class UserProfile(BaseModel):
    id: str
    email: str
    skills: List[str] = []
    experience_years: float = 0.0
    experience_level: ExperienceLevel = ExperienceLevel.junior
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    remote_preference: RemotePreference = RemotePreference.open
    ai_provider: AIProvider = AIProvider.anthropic
    has_anthropic_key: bool = False
    has_gemini_key: bool = False
    has_openai_key: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesUpdate(BaseModel):
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    experience_level: Optional[ExperienceLevel] = None
    remote_preference: Optional[RemotePreference] = None


# ── Job Schemas ────────────────────────────────────────────────────────


class JobResponse(BaseModel):
    id: str
    source: str
    source_url: str
    title: str
    company: str
    location: Optional[str] = None
    remote: bool = False
    description_normalized: Optional[str] = None
    skills_extracted: List[str] = []
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    posted_at: Optional[datetime] = None
    ingested_at: datetime

    class Config:
        from_attributes = True


class JobDetail(JobResponse):
    description_raw: Optional[str] = None


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ── Match Schemas ──────────────────────────────────────────────────────


class MatchExplanation(BaseModel):
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    experience_alignment: str = ""
    location_note: str = ""
    relevance_summary: str = ""
    improvement_tips: List[str] = []


class MatchResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    rule_score: float
    semantic_score: float
    final_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    explanation: Optional[str] = None
    computed_at: datetime
    job: Optional[JobResponse] = None
    explanation_detail: Optional[MatchExplanation] = None

    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    items: List[MatchResponse]
    total: int


# ── Settings Schemas ───────────────────────────────────────────────────


class ApiKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=1, max_length=500)


class AiProviderRequest(BaseModel):
    ai_provider: AIProvider


# ── Assist Schemas ─────────────────────────────────────────────────────


class CoverLetterRequest(BaseModel):
    job_id: str
    user_id: str


class ResumeTipsRequest(BaseModel):
    job_id: str
    user_id: str


class ResumeTipsResponse(BaseModel):
    tips: List[str]


# ── Resume Parse Output ───────────────────────────────────────────────


class ParsedResume(BaseModel):
    skills: List[str] = []
    experience_years: float = 0.0
    experience_level: ExperienceLevel = ExperienceLevel.junior
    inferred_roles: List[str] = []
    raw_text: str = ""
