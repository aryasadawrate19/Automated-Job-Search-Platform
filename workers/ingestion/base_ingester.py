"""Base class for all job ingesters."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from apps.api.schemas.schemas import ExperienceLevel


class RawJob(BaseModel):
    """Raw job representation before normalization."""
    external_id: str
    title: str
    company: str
    location: Optional[str] = None
    remote: bool = False
    description: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    posted_at: Optional[datetime] = None
    source_url: str


class NormalizedJob(BaseModel):
    """Normalized job ready for database insertion."""
    source: str
    source_url: str
    content_hash: str
    title: str
    company: str
    location: Optional[str] = None
    remote: bool = False
    description_raw: str
    description_normalized: str
    skills_extracted: List[str] = []
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    posted_at: Optional[datetime] = None


class BaseIngester(ABC):
    """Abstract interface for job aggregators."""
    
    source_name: str

    @abstractmethod
    async def fetch_raw_listings(self) -> List[RawJob]:
        """Fetch listings from the source."""
        pass

    @abstractmethod
    def normalize(self, raw: RawJob) -> NormalizedJob:
        """Normalize a raw job into the standard format."""
        pass

    def compute_hash(self, title: str, company: str, desc: str) -> str:
        """Compute SHA-256 hash for deduplication."""
        import hashlib
        content = f"{title.lower()}|{company.lower()}|{desc.lower()}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _infer_experience_level(self, title: str, desc: str) -> ExperienceLevel:
        """Simple rule-based seniority inference."""
        text = f"{title.lower()} {desc[:500].lower()}"
        if any(w in text for w in ("staff", "principal", "lead", "head")):
            return ExperienceLevel.lead
        elif any(w in text for w in ("senior", "sr", "experienced")):
            return ExperienceLevel.senior
        elif any(w in text for w in ("junior", "jr", "entry", "graduate", "intern")):
            return ExperienceLevel.junior
        return ExperienceLevel.mid
