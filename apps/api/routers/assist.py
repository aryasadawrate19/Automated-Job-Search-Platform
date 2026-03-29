"""Application Assist router — cover letter (streaming) and resume tips."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.database import get_db
from apps.api.models.models import User, Job, Match
from apps.api.schemas.schemas import CoverLetterRequest, ResumeTipsRequest, ResumeTipsResponse
from apps.api.services.application_assist import (
    stream_cover_letter,
    generate_resume_tips,
)

router = APIRouter()


@router.post("/cover-letter")
async def cover_letter(data: CoverLetterRequest, db: AsyncSession = Depends(get_db)):
    """Stream a tailored cover letter using the user's selected AI provider."""
    user = await db.get(User, uuid.UUID(data.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    job = await db.get(Job, uuid.UUID(data.job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        generator = stream_cover_letter(user, job)
        return StreamingResponse(generator, media_type="text/plain")
    except ValueError as e:
        error_data = str(e)
        if "api_key_required" in error_data:
            raise HTTPException(
                status_code=402,
                detail={"error": "api_key_required", "provider": user.ai_provider.value},
            )
        raise


@router.post("/resume-tips", response_model=ResumeTipsResponse)
async def resume_tips(data: ResumeTipsRequest, db: AsyncSession = Depends(get_db)):
    """Generate resume improvement suggestions using the user's selected AI provider."""
    user = await db.get(User, uuid.UUID(data.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    job = await db.get(Job, uuid.UUID(data.job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        tips = await generate_resume_tips(user, job)
        return ResumeTipsResponse(tips=tips)
    except ValueError as e:
        error_data = str(e)
        if "api_key_required" in error_data:
            raise HTTPException(
                status_code=402,
                detail={"error": "api_key_required", "provider": user.ai_provider.value},
            )
        raise
