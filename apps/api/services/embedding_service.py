"""Embedding service — sentence-transformers for 384-dim embeddings."""

from typing import List
from functools import lru_cache


@lru_cache(maxsize=1)
def _load_model():
    """Lazy-load the sentence-transformers model."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str) -> List[float]:
    """Generate a 384-dim embedding from text."""
    model = _load_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a batch of texts."""
    model = _load_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
    return [e.tolist() for e in embeddings]
