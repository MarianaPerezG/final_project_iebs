import re

from data.adjustment_rules import (HARD_SKILLS, HIGH_WEIGHT, LOW_WEIGHT,
                                   MAX_EDUCATION, MAX_PERFORMANCE,
                                   MIN_EDUCATION, MIN_PERFORMANCE, SOFT_SKILLS)
from data.global_skills import GLOBAL_SKILLS
from data.scoring_rules import (FAMILY_SCORES, MAX_SKILL_SCORE,
                                MIN_SKILL_SCORE, ROLE_TO_FAMILY,
                                SEMANTIC_ADJUSTMENTS)


def _clamp_score(value: int | float) -> int | float:
    return max(MIN_SKILL_SCORE, min(MAX_SKILL_SCORE, value))


def _build_adjustment_vector(role: str) -> dict[str, int]:
    adjustment_vector = {skill: 0 for skill in GLOBAL_SKILLS}

    for token in re.findall(r"[A-Za-z]+", role):
        if token not in SEMANTIC_ADJUSTMENTS:
            continue

        for skill, delta in SEMANTIC_ADJUSTMENTS[token].items():
            adjustment_vector[skill] += delta

    return adjustment_vector


def _normalize_education(education: int) -> float:
    if not isinstance(education, int):
        raise TypeError(f"education must be int (got {type(education).__name__})")
    if not (MIN_EDUCATION <= education <= MAX_EDUCATION):
        raise ValueError(
            f"education must be between {MIN_EDUCATION} and {MAX_EDUCATION} (got {education})"
        )

    return (education - 3) / 2


def _normalize_performance(performance: int) -> float:
    if not isinstance(performance, int):
        raise TypeError(f"performance must be int (got {type(performance).__name__})")
    if not (MIN_PERFORMANCE <= performance <= MAX_PERFORMANCE):
        raise ValueError(
            f"performance must be between {MIN_PERFORMANCE} and {MAX_PERFORMANCE} (got {performance})"
        )

    return (performance - 3) / 2


def _group_weights(skill: str) -> tuple[float, float]:
    if skill in SOFT_SKILLS:
        return LOW_WEIGHT, HIGH_WEIGHT

    assert skill in HARD_SKILLS
    return HIGH_WEIGHT, LOW_WEIGHT


def _build_multiplier_vector(education: int, performance: int) -> dict[str, float]:
    e = _normalize_education(education)
    p = _normalize_performance(performance)

    multiplier_vector = {}

    for skill in GLOBAL_SKILLS:
        education_weight, performance_weight = _group_weights(skill)
        multiplier_vector[skill] = 1 + e * education_weight + p * performance_weight

    return multiplier_vector


def score_role(role: str) -> dict[str, int]:
    if role not in ROLE_TO_FAMILY:
        raise ValueError(f"unknown role: {role!r}")

    base_vector = FAMILY_SCORES[ROLE_TO_FAMILY[role]]
    adjustment_vector = _build_adjustment_vector(role)

    return {
        skill: int(_clamp_score(base_vector[skill] + adjustment_vector[skill]))
        for skill in GLOBAL_SKILLS
    }


def score_employee(role: str, education: int, performance: int) -> dict[str, float]:
    role_scores = score_role(role)
    multiplier_vector = _build_multiplier_vector(education, performance)

    return {
        skill: _clamp_score(role_scores[skill] * multiplier_vector[skill])
        for skill in GLOBAL_SKILLS
    }
