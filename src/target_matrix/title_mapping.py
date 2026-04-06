import pandas as pd

from target_matrix.common import apply_role_resolver
from target_matrix.lexical_matching import resolve_role_lexical
from target_matrix.semantic_matching import resolve_role_semantic


def map_titles(df: pd.DataFrame) -> pd.DataFrame:
    lexical = apply_role_resolver(df, resolve_role_lexical)
    missing = lexical["ibm_role"].isna() | lexical["role_match"].eq("ambiguous")

    if not missing.any():
        return lexical

    semantic = apply_role_resolver(
        df.loc[missing, ["job_id", "title"]],
        resolve_role_semantic,
    )
    result = lexical.copy()
    columns = [
        "ibm_role",
        "role_match",
        "role_similarity",
        "family",
        "role_mapped",
        "family_mapped",
    ]
    result.loc[missing, columns] = semantic[columns].to_numpy()

    return result
