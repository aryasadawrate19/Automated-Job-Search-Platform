"""Users router — registration, resume upload, profile retrieval."""

import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.core.database import get_db
from apps.api.models.models import User
from apps.api.schemas.schemas import UserRegister, UserProfile
from apps.api.services.resume_parser import parse_resume
from apps.api.services.embedding_service import generate_embedding

router = APIRouter()


@router.post("/register")
async def register_user(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user by email."""
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(id=uuid.uuid4(), email=data.email)
    db.add(user)
    await db.flush()
    return {"id": str(user.id), "email": user.email}


@router.post("/resume")
async def upload_resume(
    user_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload and parse a resume (PDF or DOCX), update user profile."""
    user = await db.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    content = await file.read()
    filename = file.filename or ""

    parsed = parse_resume(content, filename)

    user.resume_raw = parsed.raw_text
    user.skills = parsed.skills
    user.experience_years = parsed.experience_years
    user.experience_level = parsed.experience_level
    user.preferred_roles = parsed.inferred_roles

    # Generate profile embedding from the full resume text
    embedding = generate_embedding(parsed.raw_text)
    user.profile_embedding = embedding

    await db.flush()
    return {
        "status": "parsed",
        "skills": parsed.skills,
        "experience_years": parsed.experience_years,
        "experience_level": parsed.experience_level.value,
        "inferred_roles": parsed.inferred_roles,
    }


@router.get("/{user_id}/profile", response_model=UserProfile)
async def get_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve user profile."""
    user = await db.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        id=str(user.id),
        email=user.email,
        skills=user.skills or [],
        experience_years=user.experience_years or 0.0,
        experience_level=user.experience_level or "junior",
        preferred_roles=user.preferred_roles or [],
        preferred_locations=user.preferred_locations or [],
        remote_preference=user.remote_preference or "open",
        ai_provider=user.ai_provider or "anthropic",
        has_anthropic_key=user.anthropic_api_key_enc is not None,
        has_gemini_key=user.gemini_api_key_enc is not None,
        has_openai_key=user.openai_api_key_enc is not None,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
