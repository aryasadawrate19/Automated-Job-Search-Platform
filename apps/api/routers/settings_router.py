"""Settings router — AI provider key management and provider selection."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.database import get_db
from apps.api.core.encryption import encrypt_key
from apps.api.models.models import User
from apps.api.schemas.schemas import ApiKeyRequest, AiProviderRequest

router = APIRouter()


# Hardcoded user_id header for now — in production, use JWT auth
def _get_user_id(request: Request) -> str:
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    return user_id


@router.post("/anthropic-key")
async def save_anthropic_key(
    data: ApiKeyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Encrypt and store the user's Anthropic API key."""
    user_id = _get_user_id(request)
    user = await db.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.anthropic_api_key_enc = encrypt_key(data.api_key)
    await db.flush()
    return {"status": "saved", "provider": "anthropic"}


@router.post("/gemini-key")
async def save_gemini_key(
    data: ApiKeyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Encrypt and store the user's Gemini API key."""
    user_id = _get_user_id(request)
    user = await db.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.gemini_api_key_enc = encrypt_key(data.api_key)
    await db.flush()
    return {"status": "saved", "provider": "gemini"}


@router.post("/openai-key")
async def save_openai_key(
    data: ApiKeyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Encrypt and store the user's OpenAI API key."""
    user_id = _get_user_id(request)
    user = await db.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.openai_api_key_enc = encrypt_key(data.api_key)
    await db.flush()
    return {"status": "saved", "provider": "openai"}


@router.post("/ai-provider")
async def set_ai_provider(
    data: AiProviderRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Set the user's active AI provider (must have a stored key)."""
    user_id = _get_user_id(request)
    user = await db.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the provider has a stored key
    key_map = {
        "anthropic": user.anthropic_api_key_enc,
        "gemini": user.gemini_api_key_enc,
        "openai": user.openai_api_key_enc,
    }
    if not key_map.get(data.ai_provider.value):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "api_key_required",
                "provider": data.ai_provider.value,
            },
        )

    user.ai_provider = data.ai_provider
    await db.flush()
    return {"status": "updated", "ai_provider": data.ai_provider.value}
