from functools import lru_cache

import torch
from sentence_transformers import SentenceTransformer, util

from config.target_titles import ROLE_TITLES
from target_matrix.common import (MatchResult, normalize_title,
                                  validate_role_titles)

MODEL_NAME = "all-MiniLM-L6-v2"  # "all-mpnet-base-v2"
ROLE_MIN_SIMILARITY = 0.78
ROLE_MIN_MARGIN = 0.05

validate_role_titles(ROLE_TITLES)


def _build_role_catalog(
    role_titles: dict[str, tuple[str, ...]],
) -> list[tuple[str, str]]:
    catalog: list[tuple[str, str]] = []

    for canonical, aliases in role_titles.items():
        for alias in aliases:
            catalog.append((canonical, normalize_title(alias)))

    return catalog


ROLE_CATALOG = _build_role_catalog(ROLE_TITLES)


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def _get_role_embeddings() -> tuple[list[tuple[str, str]], torch.Tensor]:
    model = _get_model()
    aliases = [alias for _, alias in ROLE_CATALOG]
    embeddings = model.encode(
        aliases,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    return ROLE_CATALOG, embeddings


def _score_roles(title: str) -> dict[str, float]:
    catalog, role_embeddings = _get_role_embeddings()
    model = _get_model()
    title_embedding = model.encode(
        title,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    # El producto escalar de dos vectores unitarios es igual al coseno del ángulo comprendido entre ellos
    # Si se normalizan los vectores, es más rápido utilizar el producto escalar (util.dot_score)
    # que la similitud coseno (util.cos_sim)
    # Ref: https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html
    similarities = util.dot_score(title_embedding, role_embeddings)[0].tolist()
    scores: dict[str, float] = {}

    for (canonical, _), similarity in zip(catalog, similarities, strict=False):
        best = scores.get(canonical)

        if best is None or similarity > best:
            scores[canonical] = float(similarity)

    return scores


def resolve_role_semantic(title: str) -> MatchResult:
    scores = _score_roles(title)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    if not ranked:
        return None, None, None

    best_role, best_similarity = ranked[0]
    second_similarity = ranked[1][1] if len(ranked) > 1 else None

    if best_similarity < ROLE_MIN_SIMILARITY:
        return None, None, None

    if (
        second_similarity is not None
        and best_similarity - second_similarity < ROLE_MIN_MARGIN
    ):
        return None, "ambiguous", best_similarity

    return best_role, "semantic", best_similarity
