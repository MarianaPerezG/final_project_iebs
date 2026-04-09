from pathlib import Path
from venv import logger

import pandas as pd

from config.global_skills import GLOBAL_SKILLS
from config.scoring_rules import FAMILY_CORE_SKILL
from schemas import SkillDemandConfig
from scripts.save_data import save_dataframe_to_csv
from target_matrix.demand import (
    add_demand_score,
    aggregate_demand_by_family,
    build_skill_demand_vector_by_family,
)
from target_matrix.title_mapping import map_titles


def create_skill_demand_vector_by_family(config: SkillDemandConfig) -> None:
    dataset_path = Path(config.dataset_path)
    dataset = (
        list(dataset_path.rglob("*.csv"))[0] if dataset_path.is_dir() else dataset_path
    )

    if not dataset.exists():
        raise FileNotFoundError(f"Dataset not found on: {dataset_path}")

    if dataset.suffix.lower() != ".csv":
        raise ValueError(f"File must be CSV: {dataset_path}")

    try:
        df = pd.read_csv(dataset, engine="python")
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    logger.info(f"LinkedIn demand dataset loaded successfully from: {dataset_path}")

    mapped_df = map_titles(df)
    save_dataframe_to_csv(mapped_df, config.mapped_output_path)

    family_demand_df = aggregate_demand_by_family(mapped_df)
    family_demand_df = add_demand_score(
        family_demand_df,
        group_column="family",
        frequency_column="family_frequency",
    )

    skill_demand_df = build_skill_demand_vector_by_family(
        family_demand_df,
        family_core_skill=FAMILY_CORE_SKILL,
        global_skills=list(GLOBAL_SKILLS),
    )
    save_dataframe_to_csv(skill_demand_df, config.skill_demand_output_path)

    logger.info(f"Skill demand vector saved to: {config.skill_demand_output_path}")
