import pandas as pd


def aggregate_demand_by_family(df: pd.DataFrame) -> pd.DataFrame:
    mapped = df[df["family"].notna()].copy()
    counts = mapped.groupby("family").size().rename("count").reset_index()

    counts["overall_frequency"] = counts["count"] / len(df)
    counts["family_frequency"] = counts["count"] / len(mapped)

    return counts.sort_values("count", ascending=False).reset_index(drop=True)


def aggregate_demand_by_role(df: pd.DataFrame) -> pd.DataFrame:
    mapped = df[df["ibm_role"].notna()].copy()
    counts = mapped.groupby("ibm_role").size().rename("count").reset_index()

    counts["overall_frequency"] = counts["count"] / len(df)
    counts["role_frequency"] = counts["count"] / len(mapped)

    return counts.sort_values("count", ascending=False).reset_index(drop=True)


def add_demand_score(
    df: pd.DataFrame, *, group_column: str, frequency_column: str
) -> pd.DataFrame:
    required_columns = {group_column, frequency_column}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"missing columns: {sorted(missing_columns)}")

    if df.empty:
        result = df.copy()
        result["demand_rank"] = pd.Series(dtype="int64")
        result["demand_score"] = pd.Series(dtype="float64")
        return result

    result = df.sort_values(
        by=[frequency_column, group_column],
        ascending=[False, True],
    ).reset_index(drop=True)

    total_groups = len(result)
    result["demand_rank"] = pd.RangeIndex(start=1, stop=total_groups + 1)

    if total_groups == 1:
        result["demand_score"] = 1.0
        return result

    result["demand_score"] = 1 - ((result["demand_rank"] - 1) / (total_groups - 1))

    return result


def build_skill_demand_vector_by_family(
    family_demand_df: pd.DataFrame,
    *,
    family_core_skill: dict[str, str],
    global_skills: list[str],
) -> pd.DataFrame:
    required_columns = {"family", "demand_score"}
    missing_columns = required_columns - set(family_demand_df.columns)

    if missing_columns:
        raise ValueError(f"missing columns in family demand: {sorted(missing_columns)}")

    demand = family_demand_df.copy()
    demand["skill"] = demand["family"].map(family_core_skill)

    unmapped_families = sorted(
        demand.loc[demand["skill"].isna(), "family"].dropna().unique().tolist()
    )
    if unmapped_families:
        raise ValueError(f"unmapped families in FAMILY_CORE_SKILL: {unmapped_families}")

    skill_demand = demand.groupby("skill", as_index=False).agg(
        demand_score=("demand_score", "max")
    )

    result = pd.DataFrame({"skill": global_skills})
    result = result.merge(skill_demand, on="skill", how="left")
    result["demand_score"] = result["demand_score"].fillna(0.0)

    return result
