import re

from rapidfuzz import fuzz, process

from config.target_titles import ROLE_TITLES
from target_matrix.common import (MatchResult, normalize_title,
                                  validate_role_titles)

ROLE_MIN_SIMILARITY = 90

validate_role_titles(ROLE_TITLES)


def _build_role_lookup(role_titles: dict[str, tuple[str, ...]]) -> dict[str, str]:
    lookup: dict[str, str] = {}

    for canonical, aliases in role_titles.items():
        for alias in aliases:
            lookup[normalize_title(alias)] = canonical

    return lookup


ROLE_LOOKUP = _build_role_lookup(ROLE_TITLES)


def _find_exact_roles(title: str) -> set[str]:
    matched_roles: set[str] = set()

    for key, role in ROLE_LOOKUP.items():
        if re.search(rf"\b{re.escape(key)}\b", title):
            matched_roles.add(role)

    return matched_roles


def _find_fuzzy_role(title: str) -> tuple[str | None, float | None]:
    result = process.extractOne(
        title,
        ROLE_LOOKUP.keys(),
        scorer=fuzz.token_set_ratio,
        score_cutoff=ROLE_MIN_SIMILARITY,
    )

    if result is None:
        return None, None

    key, similarity, _ = result
    return ROLE_LOOKUP[key], float(similarity)


def resolve_role_lexical(title: str) -> MatchResult:
    roles = _find_exact_roles(title)

    if len(roles) == 1:
        return next(iter(roles)), "exact", 100.0

    if len(roles) > 1:
        return None, "ambiguous", None

    role, similarity = _find_fuzzy_role(title)

    if role is None:
        return None, None, None

    return role, "fuzzy", similarity
