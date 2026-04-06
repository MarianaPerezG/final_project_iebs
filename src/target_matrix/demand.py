import pandas as pd


def summarize_family_demand(df: pd.DataFrame) -> pd.DataFrame:
    mapped = df[df["family"].notna()].copy()
    counts = mapped.groupby("family").size().rename("count").reset_index()

    counts["overall_frequency"] = counts["count"] / len(df)
    counts["family_frequency"] = counts["count"] / len(mapped)

    return counts.sort_values("count", ascending=False).reset_index(drop=True)


def summarize_role_demand(df: pd.DataFrame) -> pd.DataFrame:
    mapped = df[df["ibm_role"].notna()].copy()
    counts = mapped.groupby("ibm_role").size().rename("count").reset_index()

    counts["overall_frequency"] = counts["count"] / len(df)
    counts["role_frequency"] = counts["count"] / len(mapped)

    return counts.sort_values("count", ascending=False).reset_index(drop=True)
