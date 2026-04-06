import re
import unicodedata
from typing import Callable, TypeAlias

import pandas as pd

from config.scoring_rules import ROLE_TO_FAMILY

MatchResult: TypeAlias = tuple[str | None, str | None, float | None]
RoleResolver: TypeAlias = Callable[[str], MatchResult]


def validate_role_titles(role_titles: dict[str, tuple[str, ...]]) -> None:
    seen: dict[str, str] = {}

    for canonical, aliases in role_titles.items():
        for alias in aliases:
            normalized_alias = normalize_title(alias)

            if not normalized_alias:
                continue

            previous_canonical = seen.get(normalized_alias)

            if previous_canonical is not None and previous_canonical != canonical:
                raise ValueError(
                    f"duplicated title: {normalized_alias!r} found in "
                    f"{previous_canonical!r} and {canonical!r}"
                )

            seen[normalized_alias] = canonical


def normalize_title(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", " ", text)

    tokens = [token for token in text.split() if not token.isdigit()]
    return " ".join(tokens)


def apply_role_resolver(df: pd.DataFrame, resolve_role: RoleResolver) -> pd.DataFrame:
    required_columns = {"job_id", "title"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"missing columns: {sorted(missing_columns)}")

    result = df.copy()
    result["title"] = result["title"].fillna("").astype(str)

    normalized_titles = result["title"].map(normalize_title)
    role_matches = normalized_titles.map(resolve_role)

    result[["ibm_role", "role_match", "role_similarity"]] = pd.DataFrame(
        role_matches.tolist(),
        index=result.index,
    )

    result["family"] = result["ibm_role"].map(ROLE_TO_FAMILY)
    result["role_mapped"] = result["ibm_role"].notna()
    result["family_mapped"] = result["family"].notna()

    return result[
        [
            "job_id",
            "title",
            "ibm_role",
            "role_match",
            "role_similarity",
            "family",
            "role_mapped",
            "family_mapped",
        ]
    ].copy()
