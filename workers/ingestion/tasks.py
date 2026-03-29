"""Celery worker — job ingestion and parsing tasks."""

import asyncio
from datetime import datetime
from celery import Celery
from celery.schedules import crontab
from sqlalchemy import select

from apps.api.core.config import settings
from apps.api.core.database import async_session_factory
from apps.api.models.models import Job
from apps.api.services.skill_extractor import extract_skills_from_text
from apps.api.services.embedding_service import generate_embeddings_batch
from workers.ingestion.greenhouse_ingester import GreenhouseIngester
from workers.ingestion.lever_ingester import LeverIngester
from workers.ingestion.dedup import is_duplicate


# Initialize Celery app
celery_app = Celery(
    "ingestion_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Schedule for ingestion
celery_app.conf.beat_schedule = {
    "ingest-jobs-every-6-hours": {
        "task": "workers.ingestion.tasks.ingest_all_sources",
        "schedule": crontab(minute=0, hour="*/6"),
    },
}
celery_app.conf.timezone = "UTC"


async def process_ingester(ingester, db) -> tuple[int, int]:
    """Process all jobs from an ingester (fetch, normalize, dedup, skills, DB)."""
    raw_jobs = await ingester.fetch_raw_listings()
    
    inserts = []
    duplicates = 0
    
    for raw in raw_jobs:
        normalized = ingester.normalize(raw)
        
        # 1. Deduplication Check
        if await is_duplicate(db, normalized):
            duplicates += 1
            continue
            
        # 2. Skill Extraction (spaCy + taxonomy logic)
        skills = extract_skills_from_text(normalized.description_normalized)
        normalized.skills_extracted = skills
        inserts.append(normalized)

    if not inserts:
        return 0, duplicates

    # 3. Batch Embeddings Selection & Database Commit
    texts_to_embed = [
        f"{job.title} {job.description_normalized[:1500]}"
        for job in inserts
    ]
    # Sentence-transformers batch embedding
    embeddings = generate_embeddings_batch(texts_to_embed)

    db_jobs = []
    for norm, emb in zip(inserts, embeddings):
        j = Job(
            source=norm.source,
            source_url=norm.source_url,
            content_hash=norm.content_hash,
            title=norm.title,
            company=norm.company,
            location=norm.location,
            remote=norm.remote,
            description_raw=norm.description_raw,
            description_normalized=norm.description_normalized,
            skills_extracted=norm.skills_extracted,
            experience_level=norm.experience_level,
            salary_min=norm.salary_min,
            salary_max=norm.salary_max,
            posted_at=norm.posted_at,
            embedding=emb,
            ingested_at=datetime.utcnow()
        )
        db_jobs.append(j)
        db.add(j)

    await db.commit()
    return len(db_jobs), duplicates


async def async_ingest_all_sources():
    """Async entry point for Celery wrapper."""
    sources = [
        GreenhouseIngester("vercel"),
        GreenhouseIngester("anthropic"),
        GreenhouseIngester("stripe"),
        LeverIngester("figma"),
        LeverIngester("netflix"),
    ]

    total_inserted = 0
    total_duplicates = 0

    async with async_session_factory() as db:
        for ingester in sources:
            try:
                inserted, duplicates = await process_ingester(ingester, db)
                total_inserted += inserted
                total_duplicates += duplicates
            except Exception as e:
                print(f"Ingestion error for {ingester.source_name}: {e}")

        # Trigger batch matching worker after ingestion
        from workers.matching.tasks import compute_all_matches
        compute_all_matches.delay()

    return {"inserted": total_inserted, "duplicates": total_duplicates}


@celery_app.task(name="workers.ingestion.tasks.ingest_all_sources")
def ingest_all_sources():
    """Sync wrapper for Celery task runner."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Fallback if already in event loop
        return asyncio.ensure_future(async_ingest_all_sources())
    return loop.run_until_complete(async_ingest_all_sources())
