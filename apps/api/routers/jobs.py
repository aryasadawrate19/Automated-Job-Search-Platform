"""Jobs router — paginated listing and detail retrieval."""

import uuid
import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from apps.api.core.database import get_db
from apps.api.models.models import Job, ExperienceLevel
from apps.api.schemas.schemas import JobResponse, JobDetail, JobListResponse

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    location: Optional[str] = None,
    remote: Optional[bool] = None,
    experience_level: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Paginated job listings with optional filters."""
    query = select(Job)

    if search:
        query = query.where(
            Job.title.ilike(f"%{search}%") | Job.company.ilike(f"%{search}%")
        )
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    if remote is not None:
        query = query.where(Job.remote == remote)
    if experience_level:
        query = query.where(Job.experience_level == experience_level)

    # Total count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    query = query.order_by(Job.ingested_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    jobs = result.scalars().all()

    return JobListResponse(
        items=[
            JobResponse(
                id=str(j.id),
                source=j.source,
                source_url=j.source_url,
                title=j.title,
                company=j.company,
                location=j.location,
                remote=j.remote,
                description_normalized=j.description_normalized,
                skills_extracted=j.skills_extracted or [],
                experience_level=j.experience_level,
                salary_min=j.salary_min,
                salary_max=j.salary_max,
                posted_at=j.posted_at,
                ingested_at=j.ingested_at,
            )
            for j in jobs
        ],
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page) if total > 0 else 0,
    )


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Full job detail by ID."""
    job = await db.get(Job, uuid.UUID(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobDetail(
        id=str(job.id),
        source=job.source,
        source_url=job.source_url,
        title=job.title,
        company=job.company,
        location=job.location,
        remote=job.remote,
        description_raw=job.description_raw,
        description_normalized=job.description_normalized,
        skills_extracted=job.skills_extracted or [],
        experience_level=job.experience_level,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        posted_at=job.posted_at,
        ingested_at=job.ingested_at,
    )
