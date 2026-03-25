import re

import pandas as pd

from config.global_skills import GLOBAL_SKILLS
from config.scoring_rules import (
    FAMILY_SCORES,
    MAX_SKILL_SCORE,
    MIN_SKILL_SCORE,
    ROLE_TO_FAMILY,
    SEMANTIC_ADJUSTMENTS,
)


def _clamp_score(value: int) -> int:
    return max(MIN_SKILL_SCORE, min(MAX_SKILL_SCORE, value))


def _build_adjustment_vector(role: str) -> dict[str, int]:
    adjustment_vector = {skill: 0 for skill in GLOBAL_SKILLS}

    for token in re.findall(r"[A-Za-z]+", role):
        if token not in SEMANTIC_ADJUSTMENTS:
            continue

        for skill, delta in SEMANTIC_ADJUSTMENTS[token].items():
            adjustment_vector[skill] += delta

    return adjustment_vector


def _score_role(role: str) -> dict[str, int]:
    base_vector = FAMILY_SCORES[ROLE_TO_FAMILY[role]]
    adjustment_vector = _build_adjustment_vector(role)

    return {
        skill: _clamp_score(base_vector[skill] + adjustment_vector[skill])
        for skill in GLOBAL_SKILLS
    }


def score_role(role: str) -> dict[str, int]:
    if role not in ROLE_TO_FAMILY:
        raise ValueError(f"Unknown role: {role!r}")

    return _score_role(role)


def score_roles(roles: pd.Series) -> pd.DataFrame:
    unknown_roles = sorted(set(roles.dropna().unique()) - set(ROLE_TO_FAMILY))
    if unknown_roles:
        raise ValueError(f"Unknown roles: {unknown_roles}")

    return pd.DataFrame([_score_role(role) for role in roles], index=roles.index)
