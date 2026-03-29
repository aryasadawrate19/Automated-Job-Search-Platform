"""Deduplication logic — SHA256 and fuzzy matching."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from rapidfuzz import fuzz

from apps.api.models.models import Job
from workers.ingestion.base_ingester import NormalizedJob


async def is_duplicate(db: AsyncSession, job: NormalizedJob) -> bool:
    """
    Check if a job is a duplicate based on:
    1. Exact hash match
    2. Fuzzy match on title + company
    """
    # 1. Exact hash check
    existing_hash = await db.execute(select(Job.id).where(Job.content_hash == job.content_hash))
    if existing_hash.scalar_one_or_none():
        return True

    # 2. Source URL check
    existing_url = await db.execute(select(Job.id).where(Job.source_url == job.source_url))
    if existing_url.scalar_one_or_none():
        return True

    # 3. Fuzzy match check
    # In a very large DB, we shouldn't fetch all jobs. We assume we run
    # this against recent jobs (last 30 days) from the DB.
    # For now, we'll fetch jobs from the same company to check fuzzily.
    recent_jobs = await db.execute(
        select(Job.title, Job.company)
        .where(Job.company == job.company)
        .limit(100)
    )
    
    threshold = 92
    incoming_str = f"{job.title} {job.company}".lower()
    
    for row in recent_jobs:
        existing_str = f"{row.title} {row.company}".lower()
        score = fuzz.ratio(incoming_str, existing_str)
        if score >= threshold:
            return True

    return False
