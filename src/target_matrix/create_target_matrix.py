from pathlib import Path
from venv import logger

import pandas as pd

from config.global_skills import GLOBAL_SKILLS
from schemas import TargetMatrixConfig
from scripts.save_data import save_dataframe_to_csv
from target_matrix.builder import TargetMatrixBuilder
from target_matrix.goals import get_company_goals


def create_target_matrix(config: TargetMatrixConfig) -> None:
    skill_matrix_path = Path(config.skill_matrix_path)
    skill_demand_path = Path(config.skill_demand_path)

    if not skill_matrix_path.exists():
        raise FileNotFoundError(f"Skill matrix not found on: {skill_matrix_path}")

    if not skill_demand_path.exists():
        raise FileNotFoundError(
            f"Skill demand vector not found on: {skill_demand_path}"
        )

    try:
        skill_matrix_df = pd.read_csv(skill_matrix_path)
        skill_demand_df = pd.read_csv(skill_demand_path)

    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    builder = TargetMatrixBuilder(global_skills=list(GLOBAL_SKILLS))
    result = builder.build_from_family(
        skill_matrix_df=skill_matrix_df,
        skill_demand_df=skill_demand_df,
        company_goals=get_company_goals(),
    )

    save_dataframe_to_csv(result.matrix, config.final_output_path)
    logger.info(f"Final target matrix saved to: {config.final_output_path}")
