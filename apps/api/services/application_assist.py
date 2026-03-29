"""Application assist — multi-provider AI for cover letters and resume tips."""

from typing import AsyncGenerator, List

from apps.api.core.encryption import decrypt_key
from apps.api.models.models import User, Job


def _get_user_api_key(user: User) -> str:
    """Decrypt and return the API key for the user's selected provider."""
    provider = user.ai_provider.value if user.ai_provider else "anthropic"

    key_map = {
        "anthropic": user.anthropic_api_key_enc,
        "gemini": user.gemini_api_key_enc,
        "openai": user.openai_api_key_enc,
    }

    encrypted_key = key_map.get(provider)
    if not encrypted_key:
        raise ValueError(f"api_key_required:{provider}")

    return decrypt_key(encrypted_key)


def _build_cover_letter_prompt(user: User, job: Job) -> str:
    """Build the prompt for cover letter generation."""
    skills = ", ".join(user.skills or [])
    roles = ", ".join(user.preferred_roles or [])

    return (
        f"Write a professional, tailored cover letter for the following job:\n\n"
        f"Job Title: {job.title}\n"
        f"Company: {job.company}\n"
        f"Location: {job.location or 'Not specified'}\n"
        f"Description: {(job.description_normalized or job.description_raw or '')[:2000]}\n\n"
        f"Applicant Profile:\n"
        f"- Skills: {skills}\n"
        f"- Experience: {user.experience_years} years ({user.experience_level.value}-level)\n"
        f"- Preferred Roles: {roles}\n\n"
        f"Write a compelling 3-4 paragraph cover letter that highlights relevant skills "
        f"and experience. Be specific about how the applicant's background matches the "
        f"role requirements. Keep the tone professional but engaging."
    )


def _build_resume_tips_prompt(user: User, job: Job) -> str:
    """Build the prompt for resume improvement suggestions."""
    skills = ", ".join(user.skills or [])
    job_skills = ", ".join(job.skills_extracted or [])

    return (
        f"Given the following job listing and applicant profile, generate exactly 3 "
        f"bullet-point resume improvements.\n\n"
        f"Job Title: {job.title}\n"
        f"Company: {job.company}\n"
        f"Required Skills: {job_skills}\n"
        f"Description: {(job.description_normalized or '')[:1500]}\n\n"
        f"Applicant Skills: {skills}\n"
        f"Experience: {user.experience_years} years ({user.experience_level.value}-level)\n\n"
        f"Provide 3 specific, actionable resume improvements. Each should be a single "
        f"sentence starting with a verb. Focus on missing skills and experience gaps."
    )


async def stream_cover_letter(user: User, job: Job) -> AsyncGenerator[str, None]:
    """Stream a cover letter using the user's selected AI provider."""
    api_key = _get_user_api_key(user)
    provider = user.ai_provider.value if user.ai_provider else "anthropic"
    prompt = _build_cover_letter_prompt(user, job)

    if provider == "anthropic":
        yield_from = _stream_anthropic(api_key, prompt)
    elif provider == "gemini":
        yield_from = _stream_gemini(api_key, prompt)
    elif provider == "openai":
        yield_from = _stream_openai(api_key, prompt)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    async for chunk in yield_from:
        yield chunk


async def _stream_anthropic(api_key: str, prompt: str) -> AsyncGenerator[str, None]:
    """Stream from Anthropic (claude-sonnet-4-20250514)."""
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=api_key)
    async with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def _stream_gemini(api_key: str, prompt: str) -> AsyncGenerator[str, None]:
    """Stream from Google Gemini (gemini-2.0-flash)."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt, stream=True)

    for chunk in response:
        if chunk.text:
            yield chunk.text


async def _stream_openai(api_key: str, prompt: str) -> AsyncGenerator[str, None]:
    """Stream from OpenAI (gpt-4o)."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


async def generate_resume_tips(user: User, job: Job) -> List[str]:
    """Generate resume improvement tips using the user's selected AI provider."""
    api_key = _get_user_api_key(user)
    provider = user.ai_provider.value if user.ai_provider else "anthropic"
    prompt = _build_resume_tips_prompt(user, job)

    if provider == "anthropic":
        return await _tips_anthropic(api_key, prompt)
    elif provider == "gemini":
        return await _tips_gemini(api_key, prompt)
    elif provider == "openai":
        return await _tips_openai(api_key, prompt)
    else:
        raise ValueError(f"Unknown provider: {provider}")


async def _tips_anthropic(api_key: str, prompt: str) -> List[str]:
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_bullet_points(message.content[0].text)


async def _tips_gemini(api_key: str, prompt: str) -> List[str]:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return _parse_bullet_points(response.text)


async def _tips_openai(api_key: str, prompt: str) -> List[str]:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )
    return _parse_bullet_points(response.choices[0].message.content or "")


def _parse_bullet_points(text: str) -> List[str]:
    """Parse bullet points from AI response."""
    lines = text.strip().split("\n")
    tips = []
    for line in lines:
        line = line.strip()
        if line and (line.startswith("-") or line.startswith("•") or line[0].isdigit()):
            cleaned = line.lstrip("-•0123456789.) ").strip()
            if cleaned:
                tips.append(cleaned)
    return tips[:5] if tips else [text.strip()[:300]]
