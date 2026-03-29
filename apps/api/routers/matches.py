"""Matches router — user matches with explanations."""

import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from apps.api.core.database import get_db
from apps.api.models.models import Match, Job
from apps.api.schemas.schemas import MatchResponse, MatchListResponse, MatchExplanation, JobResponse

router = APIRouter()


@router.get("/{user_id}", response_model=MatchListResponse)
async def get_matches(
    user_id: str,
    request: Request,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Top N matches for a user, ranked by final_score descending."""
    redis = request.app.state.redis
    cache_key = f"matches:{user_id}"

    # Check Redis cache
    cached = await redis.get(cache_key)
    if cached:
        return MatchListResponse(**json.loads(cached))

    query = (
        select(Match)
        .options(joinedload(Match.job))
        .where(Match.user_id == uuid.UUID(user_id))
        .order_by(Match.final_score.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    matches = result.unique().scalars().all()

    items = []
    for m in matches:
        explanation_detail = None
        if m.explanation:
            try:
                explanation_detail = MatchExplanation(**json.loads(m.explanation))
            except (json.JSONDecodeError, TypeError):
                pass

        job_resp = None
        if m.job:
            job_resp = JobResponse(
                id=str(m.job.id),
                source=m.job.source,
                source_url=m.job.source_url,
                title=m.job.title,
                company=m.job.company,
                location=m.job.location,
                remote=m.job.remote,
                description_normalized=m.job.description_normalized,
                skills_extracted=m.job.skills_extracted or [],
                experience_level=m.job.experience_level,
                salary_min=m.job.salary_min,
                salary_max=m.job.salary_max,
                posted_at=m.job.posted_at,
                ingested_at=m.job.ingested_at,
            )

        items.append(
            MatchResponse(
                id=str(m.id),
                user_id=str(m.user_id),
                job_id=str(m.job_id),
                rule_score=m.rule_score,
                semantic_score=m.semantic_score,
                final_score=m.final_score,
                matched_skills=m.matched_skills or [],
                missing_skills=m.missing_skills or [],
                explanation=m.explanation,
                computed_at=m.computed_at,
                job=job_resp,
                explanation_detail=explanation_detail,
            )
        )

    response = MatchListResponse(items=items, total=len(items))

    # Cache for 1 hour
    await redis.setex(cache_key, 3600, response.model_dump_json())

    return response


@router.get("/{user_id}/{job_id}", response_model=MatchResponse)
async def get_match_detail(
    user_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Single match detail with full explanation."""
    query = (
        select(Match)
        .options(joinedload(Match.job))
        .where(
            Match.user_id == uuid.UUID(user_id),
            Match.job_id == uuid.UUID(job_id),
        )
    )
    result = await db.execute(query)
    m = result.unique().scalar_one_or_none()

    if not m:
        raise HTTPException(status_code=404, detail="Match not found")

    explanation_detail = None
    if m.explanation:
        try:
            explanation_detail = MatchExplanation(**json.loads(m.explanation))
        except (json.JSONDecodeError, TypeError):
            pass

    job_resp = None
    if m.job:
        job_resp = JobResponse(
            id=str(m.job.id),
            source=m.job.source,
            source_url=m.job.source_url,
            title=m.job.title,
            company=m.job.company,
            location=m.job.location,
            remote=m.job.remote,
            description_normalized=m.job.description_normalized,
            skills_extracted=m.job.skills_extracted or [],
            experience_level=m.job.experience_level,
            salary_min=m.job.salary_min,
            salary_max=m.job.salary_max,
            posted_at=m.job.posted_at,
            ingested_at=m.job.ingested_at,
        )

    return MatchResponse(
        id=str(m.id),
        user_id=str(m.user_id),
        job_id=str(m.job_id),
        rule_score=m.rule_score,
        semantic_score=m.semantic_score,
        final_score=m.final_score,
        matched_skills=m.matched_skills or [],
        missing_skills=m.missing_skills or [],
        explanation=m.explanation,
        computed_at=m.computed_at,
        job=job_resp,
        explanation_detail=explanation_detail,
    )
