"""Skill extraction — spaCy NER + taxonomy fuzzy matching."""

import json
import os
from typing import List
from functools import lru_cache
from rapidfuzz import fuzz, process


TAXONOMY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "workers", "ingestion", "skills_taxonomy.json",
)


@lru_cache(maxsize=1)
def _load_taxonomy() -> List[str]:
    """Load the curated skills taxonomy."""
    try:
        with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


@lru_cache(maxsize=1)
def _load_spacy_model():
    """Load the spaCy model (lazy, cached)."""
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Model not installed — return None
        return None


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from text using:
    1. spaCy NER + noun chunk extraction
    2. Fuzzy matching against the skills taxonomy (threshold 85)
    """
    taxonomy = _load_taxonomy()
    if not taxonomy:
        return []

    # Build a set of candidate tokens from the text
    candidates = set()

    # Use spaCy for NER and noun chunks
    nlp = _load_spacy_model()
    if nlp:
        doc = nlp(text[:100_000])  # Cap text length for performance

        # Named entities
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT", "WORK_OF_ART", "LANGUAGE", "NORP"):
                candidates.add(ent.text.strip().lower())

        # Noun chunks
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip().lower()
            if 1 <= len(chunk_text.split()) <= 4:
                candidates.add(chunk_text)
    else:
        # Fallback: simple word extraction if spaCy not available
        words = text.lower().split()
        candidates = set(w.strip(".,;:!?()[]{}\"'") for w in words if len(w) > 2)

    # Also add individual words from the text for single-word skill matching
    for word in text.lower().split():
        cleaned = word.strip(".,;:!?()[]{}\"'/-")
        if len(cleaned) > 1:
            candidates.add(cleaned)

    # Fuzzy match candidates against taxonomy
    matched_skills = set()
    taxonomy_lower = [s.lower() for s in taxonomy]

    for candidate in candidates:
        if len(candidate) < 2:
            continue
        result = process.extractOne(
            candidate,
            taxonomy_lower,
            scorer=fuzz.ratio,
            score_cutoff=85,
        )
        if result:
            matched_skill = result[0]
            matched_skills.add(matched_skill)

    return sorted(list(matched_skills))
