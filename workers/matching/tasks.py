"""Celery worker — batch matching computations."""

import asyncio
import json
from datetime import datetime
from celery import Celery
from sqlalchemy import select

from apps.api.core.config import settings
from apps.api.core.database import async_session_factory
from apps.api.models.models import Job, User, Match
from apps.api.services.matching_engine import (
    compute_rule_score,
    compute_semantic_score,
    compute_final_score,
)
from apps.api.services.explainability import generate_explanation

# Initialize Celery app
celery_app = Celery(
    "matching_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


async def async_compute_matches_for_user(user: User, limit: int = 500):
    """Compute matches for a single user against the database of jobs."""
    async with async_session_factory() as db:
        # We limit the matching against the most recent jobs in a production 
        # system. Here we'll search top `limit` using pgvector IVFFlat index.
        
        # 1. Broad candidate generation (ANN Search)
        jobs_query = (
            select(Job)
            .order_by(Job.embedding.cosine_distance(user.profile_embedding))
            .limit(limit)
        )
        result = await db.execute(jobs_query)
        candidate_jobs = result.scalars().all()

        match_records = []
        for job in candidate_jobs:
            # 2. Re-ranking: Rule-based computation
            rule_score, matched_skills, missing_skills = compute_rule_score(
                user_skills=user.skills,
                job_skills=job.skills_extracted,
                user_level=user.experience_level.value,
                job_level=job.experience_level.value if job.experience_level else None,
                user_locations=user.preferred_locations,
                user_remote_pref=user.remote_preference.value,
                job_location=job.location,
                job_remote=job.remote,
            )

            # Re-compute semantic exactly for weighting
            semantic_score = compute_semantic_score(user.profile_embedding, job.embedding)
            final_score = compute_final_score(rule_score, semantic_score)

            # Skip poor matches
            if final_score < 0.3:
                continue

            # 3. Explainability layer
            explanation = generate_explanation(
                job_title=job.title,
                company=job.company,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                user_level=user.experience_level.value,
                job_level=job.experience_level.value if job.experience_level else None,
                user_remote_pref=user.remote_preference.value,
                job_remote=job.remote,
                job_location=job.location,
                rule_score=rule_score,
                semantic_score=semantic_score,
            )

            # 4. Upsert Match record
            existing = await db.execute(
                select(Match).where(
                    Match.user_id == user.id,
                    Match.job_id == job.id,
                )
            )
            m = existing.scalar_one_or_none()

            if m:
                m.rule_score = rule_score
                m.semantic_score = semantic_score
                m.final_score = final_score
                m.matched_skills = matched_skills
                m.missing_skills = missing_skills
                m.explanation = explanation.model_dump_json()
                m.computed_at = datetime.utcnow()
            else:
                m = Match(
                    user_id=user.id,
                    job_id=job.id,
                    rule_score=rule_score,
                    semantic_score=semantic_score,
                    final_score=final_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    explanation=explanation.model_dump_json(),
                    computed_at=datetime.utcnow()
                )
                db.add(m)
                
            match_records.append(m)

        await db.commit()
        
        # Clear user's match cache in Redis
        # Import moved to inside to avoid circular imports if any
        import redis.asyncio as aioredis
        redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis.delete(f"matches:{user.id}")
        await redis.close()
        
        return len(match_records)


async def async_compute_all_matches():
    """Batch re-computation for all active users."""
    total_computed = 0
    async with async_session_factory() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

        for user in users:
            try:
                computed = await async_compute_matches_for_user(user)
                total_computed += computed
            except Exception as e:
                print(f"Error computing matches for user {user.id}: {e}")

    return total_computed


@celery_app.task(name="workers.matching.tasks.compute_user_matches")
def compute_user_matches(user_id: str):
    """Triggered dynamically when a user updates their profile."""
    loop = asyncio.get_event_loop()
    
    async def _run():
        async with async_session_factory() as db:
            from uuid import UUID
            user = await db.get(User, UUID(user_id))
            if user:
                return await async_compute_matches_for_user(user)
        return 0

    if loop.is_running():
        return asyncio.ensure_future(_run())
    return loop.run_until_complete(_run())


@celery_app.task(name="workers.matching.tasks.compute_all_matches")
def compute_all_matches():
    """Triggered periodically or after large ingestion."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(async_compute_all_matches())
    return loop.run_until_complete(async_compute_all_matches())
