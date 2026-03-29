"""Hybrid matching engine — rule-based + semantic scoring."""

from typing import List, Tuple, Optional
import numpy as np


def compute_rule_score(
    user_skills: List[str],
    job_skills: List[str],
    user_level: str,
    job_level: Optional[str],
    user_locations: List[str],
    user_remote_pref: str,
    job_location: Optional[str],
    job_remote: bool,
) -> Tuple[float, List[str], List[str]]:
    """
    Compute rule-based match score.

    Returns: (score, matched_skills, missing_skills)

    Formula:
        skill_overlap = |user ∩ job| / |job|
        experience_score = 1.0 if match, 0.6 if adjacent, 0.2 if far
        location_score = 1.0 if remote match or location match, 0.4 if open, 0.0 if mismatch
        rule_score = 0.5 * skill_overlap + 0.3 * experience_score + 0.2 * location_score
    """
    # Skill overlap
    user_set = set(s.lower() for s in user_skills)
    job_set = set(s.lower() for s in job_skills)

    matched = user_set & job_set
    missing = job_set - user_set

    skill_overlap = len(matched) / len(job_set) if job_set else 0.0

    # Experience score
    level_order = {"junior": 0, "mid": 1, "senior": 2, "lead": 3}
    user_idx = level_order.get(user_level, 0)
    job_idx = level_order.get(job_level, 1) if job_level else 1

    level_diff = abs(user_idx - job_idx)
    if level_diff == 0:
        experience_score = 1.0
    elif level_diff == 1:
        experience_score = 0.6
    else:
        experience_score = 0.2

    # Location score
    location_score = 0.0
    if job_remote and user_remote_pref in ("only", "preferred"):
        location_score = 1.0
    elif job_remote and user_remote_pref == "open":
        location_score = 0.8
    elif job_location and any(
        loc.lower() in (job_location or "").lower() for loc in user_locations
    ):
        location_score = 1.0
    elif user_remote_pref == "open":
        location_score = 0.4
    else:
        location_score = 0.0

    # Weighted combination
    rule_score = 0.5 * skill_overlap + 0.3 * experience_score + 0.2 * location_score

    return (
        round(min(rule_score, 1.0), 4),
        sorted(list(matched)),
        sorted(list(missing)),
    )


def compute_semantic_score(
    user_embedding: List[float],
    job_embedding: List[float],
) -> float:
    """
    Compute cosine similarity between user and job embeddings.
    Both embeddings are assumed to be normalized (L2 norm = 1).
    """
    if not user_embedding or not job_embedding:
        return 0.0

    u = np.array(user_embedding, dtype=np.float32)
    j = np.array(job_embedding, dtype=np.float32)

    # Cosine similarity (dot product of normalized vectors)
    similarity = float(np.dot(u, j))

    # Clamp to [0, 1]
    return round(max(0.0, min(similarity, 1.0)), 4)


def compute_final_score(rule_score: float, semantic_score: float) -> float:
    """
    Compute weighted final score.
    final = 0.5 * rule_score + 0.5 * semantic_score
    """
    return round(0.5 * rule_score + 0.5 * semantic_score, 4)
