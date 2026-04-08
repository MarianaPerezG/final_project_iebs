"""Semantic similarity scoring for course recommendations using NLP embeddings."""

from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def compute_semantic_similarity(text1: str, text2: str) -> float:
    try:
        model = _get_model()

        # Use convert_to_tensor=False to get numpy arrays (faster, no torch overhead)
        emb1 = model.encode(
            text1,
            convert_to_tensor=False,
            normalize_embeddings=True,
        )
        emb2 = model.encode(
            text2,
            convert_to_tensor=False,
            normalize_embeddings=True,
        )

        # Simple numpy dot product (very fast, no torch overhead)
        similarity = float(np.dot(emb1, emb2))

        similarity = max(0.0, min(1.0, similarity))

        return similarity

    except Exception as e:
        import logging

        logging.warning(f"Semantic similarity computation failed: {e}")
        return 0.5


def batch_compute_semantic_similarity(text1: str, texts2: list) -> list:
    try:
        model = _get_model()

        emb1 = model.encode(
            text1,
            convert_to_tensor=False,
            normalize_embeddings=True,
        )
        emb2_list = model.encode(
            texts2,
            convert_to_tensor=False,
            normalize_embeddings=True,
        )

        # Batch dot product with numpy
        similarities = np.dot(emb2_list, emb1).tolist()

        similarities = [max(0.0, min(1.0, sim)) for sim in similarities]

        return similarities

    except Exception as e:
        import logging

        logging.warning(f"Batch semantic similarity computation failed: {e}")
        return [0.5] * len(texts2)
