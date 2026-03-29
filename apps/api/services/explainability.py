"""Explainability engine — template-based explanations for match results."""

import json
from typing import List
from collections import Counter

from apps.api.schemas.schemas import MatchExplanation


def generate_explanation(
    job_title: str,
    company: str,
    matched_skills: List[str],
    missing_skills: List[str],
    user_level: str,
    job_level: str,
    user_remote_pref: str,
    job_remote: bool,
    job_location: str,
    rule_score: float,
    semantic_score: float,
) -> MatchExplanation:
    """
    Generate a structured, template-based match explanation (no LLM).
    """
    # ── Experience alignment ───────────────────────────────────────────
    level_order = {"junior": 0, "mid": 1, "senior": 2, "lead": 3}
    u_idx = level_order.get(user_level, 0)
    j_idx = level_order.get(job_level or "mid", 1)
    diff = u_idx - j_idx

    if diff == 0:
        experience_alignment = f"Strong match — your {user_level}-level experience aligns with the job requirements."
    elif diff == 1:
        experience_alignment = f"Good fit — you are {user_level}-level and the role targets {job_level}-level engineers. You may be slightly overqualified."
    elif diff == -1:
        experience_alignment = f"Slight mismatch — the job requires {job_level}-level experience, you are currently at {user_level} level. This could be a stretch opportunity."
    else:
        experience_alignment = f"Significant gap — the role targets {job_level}-level but your profile is {user_level}-level."

    # ── Location note ──────────────────────────────────────────────────
    if job_remote:
        location_note = "This is a remote position, matching your preferences." if user_remote_pref in ("only", "preferred") else "This is a remote position."
    elif job_location:
        location_note = f"This position is located in {job_location}."
    else:
        location_note = "Location information not available."

    # ── Relevance summary ──────────────────────────────────────────────
    n_matched = len(matched_skills)
    n_missing = len(missing_skills)
    top_skills = ", ".join(matched_skills[:3]) if matched_skills else "none"
    remote_str = "remote" if job_remote else "onsite"

    relevance_summary = (
        f"This {job_title} role at {company} aligns with {n_matched} of your skills "
        f"including {top_skills}. "
        f"The position is {remote_str} and targets {job_level or 'mid'}-level engineers. "
    )
    if n_missing > 0:
        missing_str = ", ".join(missing_skills[:5])
        relevance_summary += f"You are missing {n_missing} required skill{'s' if n_missing != 1 else ''}: {missing_str}."
    else:
        relevance_summary += "Your skill profile is a strong match for all listed requirements."

    # ── Improvement tips ───────────────────────────────────────────────
    improvement_tips = []
    for skill in missing_skills[:5]:
        improvement_tips.append(f"Consider adding {skill} to your profile to improve this match.")
    if not improvement_tips:
        improvement_tips.append("Your profile is well-aligned! Keep your skills section updated.")

    return MatchExplanation(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        experience_alignment=experience_alignment,
        location_note=location_note,
        relevance_summary=relevance_summary,
        improvement_tips=improvement_tips,
    )


def aggregate_improvement_tips(
    all_missing_skills: List[List[str]],
    top_n: int = 5,
) -> List[str]:
    """
    Across top N matches, find the most impactful skill gaps.
    Sort by frequency to surface the most commonly required missing skills.
    """
    counter = Counter()
    for missing in all_missing_skills:
        for skill in missing:
            counter[skill.lower()] += 1

    tips = []
    for skill, count in counter.most_common(top_n):
        tips.append(
            f"Learn {skill} — required in {count} of your top matches."
        )
    return tips
