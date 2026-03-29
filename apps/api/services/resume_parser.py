"""Resume parser — extract text, skills, experience from PDF/DOCX without LLMs."""

import re
from typing import List, Tuple, Optional
from datetime import datetime
from io import BytesIO

from apps.api.schemas.schemas import ParsedResume, ExperienceLevel
from apps.api.services.skill_extractor import extract_skills_from_text


# ── Section detection patterns ─────────────────────────────────────────

SECTION_PATTERNS = {
    "skills": re.compile(
        r"(?:^|\n)\s*(?:technical\s+)?skills?\s*[:\-—]?\s*\n",
        re.IGNORECASE | re.MULTILINE,
    ),
    "experience": re.compile(
        r"(?:^|\n)\s*(?:work\s+|professional\s+)?experience\s*[:\-—]?\s*\n",
        re.IGNORECASE | re.MULTILINE,
    ),
    "education": re.compile(
        r"(?:^|\n)\s*education\s*[:\-—]?\s*\n",
        re.IGNORECASE | re.MULTILINE,
    ),
    "summary": re.compile(
        r"(?:^|\n)\s*(?:summary|profile|objective|about)\s*[:\-—]?\s*\n",
        re.IGNORECASE | re.MULTILINE,
    ),
}

# Date extraction patterns
DATE_RANGE_PATTERN = re.compile(
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4})"
    r"\s*[-–—to]+\s*"
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|[Pp]resent|[Cc]urrent)",
    re.IGNORECASE,
)

YEAR_RANGE_PATTERN = re.compile(
    r"(\d{4})\s*[-–—to]+\s*(\d{4}|[Pp]resent|[Cc]urrent)",
    re.IGNORECASE,
)

# Common job title patterns
TITLE_PATTERNS = re.compile(
    r"(?:^|\n)\s*(?:(?:Senior|Junior|Lead|Staff|Principal|Associate|Chief)\s+)?"
    r"(?:Software|Backend|Frontend|Full[- ]?Stack|Data|ML|AI|DevOps|Cloud|Mobile|QA|"
    r"Product|Project|Engineering|Infrastructure|Platform|Security|Systems)\s+"
    r"(?:Engineer|Developer|Architect|Manager|Analyst|Scientist|Designer|Specialist|Intern)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    import fitz  # PyMuPDF

    doc = fitz.open(stream=content, filetype="pdf")
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)


def _extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    from docx import Document

    doc = Document(BytesIO(content))
    return "\n".join(para.text for para in doc.paragraphs)


def _extract_date_ranges(text: str) -> List[Tuple[datetime, Optional[datetime]]]:
    """Extract date ranges from experience section."""
    ranges = []

    for match in DATE_RANGE_PATTERN.finditer(text):
        parts = re.split(r"\s*[-–—to]+\s*", match.group(), maxsplit=1)
        if len(parts) == 2:
            try:
                import dateparser

                start = dateparser.parse(parts[0].strip())
                end_str = parts[1].strip()
                if end_str.lower() in ("present", "current"):
                    end = datetime.now()
                else:
                    end = dateparser.parse(end_str)
                if start and end:
                    ranges.append((start, end))
            except Exception:
                pass

    # Fallback: year ranges
    if not ranges:
        for match in YEAR_RANGE_PATTERN.finditer(text):
            try:
                start_year = int(match.group(1))
                end_str = match.group(2)
                if end_str.lower() in ("present", "current"):
                    end_year = datetime.now().year
                else:
                    end_year = int(end_str)
                start = datetime(start_year, 1, 1)
                end = datetime(end_year, 12, 31)
                ranges.append((start, end))
            except (ValueError, TypeError):
                pass

    return ranges


def _compute_experience_years(ranges: List[Tuple[datetime, Optional[datetime]]]) -> float:
    """Compute total years of experience from date ranges, allowing overlaps."""
    if not ranges:
        return 0.0

    total_days = 0
    for start, end in ranges:
        if end:
            delta = (end - start).days
            total_days += max(delta, 0)

    return round(total_days / 365.25, 1)


def _classify_seniority(years: float) -> ExperienceLevel:
    """Classify seniority from years of experience."""
    if years < 2:
        return ExperienceLevel.junior
    elif years < 5:
        return ExperienceLevel.mid
    elif years < 8:
        return ExperienceLevel.senior
    else:
        return ExperienceLevel.lead


def _extract_job_titles(text: str) -> List[str]:
    """Extract job titles from experience section."""
    titles = set()
    for match in TITLE_PATTERNS.finditer(text):
        title = match.group().strip()
        titles.add(title.title())
    return list(titles)[:10]  # Cap at 10 titles


def parse_resume(content: bytes, filename: str) -> ParsedResume:
    """
    Parse an uploaded resume file.

    Pipeline:
    1. Text extraction (PDF/DOCX)
    2. Skills extraction (spaCy + taxonomy)
    3. Experience parsing (date ranges → years → seniority)
    4. Role inference (job title extraction)
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        raw_text = _extract_text_from_pdf(content)
    elif ext in ("docx", "doc"):
        raw_text = _extract_text_from_docx(content)
    else:
        # Attempt plain text fallback
        raw_text = content.decode("utf-8", errors="ignore")

    # Normalize whitespace
    normalized_text = re.sub(r"\s+", " ", raw_text).strip()

    # Extract skills using shared taxonomy pipeline
    skills = extract_skills_from_text(normalized_text)

    # Extract date ranges and compute experience
    date_ranges = _extract_date_ranges(raw_text)
    experience_years = _compute_experience_years(date_ranges)
    experience_level = _classify_seniority(experience_years)

    # Extract job titles for role inference
    inferred_roles = _extract_job_titles(raw_text)

    return ParsedResume(
        skills=skills,
        experience_years=experience_years,
        experience_level=experience_level,
        inferred_roles=inferred_roles,
        raw_text=normalized_text,
    )
