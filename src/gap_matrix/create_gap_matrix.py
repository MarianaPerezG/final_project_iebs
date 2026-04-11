import logging
from pathlib import Path

import pandas as pd

from config.global_skills import GLOBAL_SKILLS
from schemas import GapMatrixConfig
from scripts.save_data import save_dataframe_to_csv


def create_gap_matrix(
    config: GapMatrixConfig,
) -> None:
    skill_matrix_path = Path(config.skill_matrix_path)
    target_matrix_path = Path(config.target_matrix_path)

    if not skill_matrix_path.exists():
        raise FileNotFoundError(f"Skill matrix not found on: {skill_matrix_path}")

    if not target_matrix_path.exists():
        raise FileNotFoundError(f"Target matrix not found on: {target_matrix_path}")

    try:
        skill_matrix_df = pd.read_csv(skill_matrix_path)
        target_matrix_df = pd.read_csv(target_matrix_path)

    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    merge_keys = ["EmployeeNumber", "JobRole"]

    for key in merge_keys:
        if key not in skill_matrix_df.columns:
            raise ValueError(f"Missing column in skill matrix: {key}")

        if key not in target_matrix_df.columns:
            raise ValueError(f"Missing column in target matrix: {key}")

    merged = skill_matrix_df.merge(
        target_matrix_df,
        on=merge_keys,
        how="inner",
        suffixes=("_skill", "_target"),
    )

    if merged.empty:
        raise ValueError("Gap matrix merge produced no rows")

    result = merged[merge_keys].copy()

    if "JobLevel" in merged.columns:
        result["JobLevel"] = merged["JobLevel"]

    if "family" in merged.columns:
        result["family"] = merged["family"]

    for skill in GLOBAL_SKILLS:
        skill_col = f"{skill}_skill"
        target_col = f"{skill}_target"

        if skill_col not in merged.columns:
            raise ValueError(f"Missing skill column in skill matrix merge: {skill_col}")

        if target_col not in merged.columns:
            raise ValueError(
                f"Missing skill column in target matrix merge: {target_col}"
            )

        result[skill] = (
            (merged[target_col].astype(float) - merged[skill_col].astype(float))
            .clip(lower=0.0)
            .round(3)
        )

    save_dataframe_to_csv(result, config.final_output_path)
    logging.info(f"Final gap matrix saved to: {config.final_output_path}")
