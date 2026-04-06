from pathlib import Path
from venv import logger

import pandas as pd

from skill_matrix.builder import SkillMatrixBuilder
from schemas import SkillMatrixConfig
from scripts.save_data import save_dataframe_to_csv


def create_skill_matrix(
    global_skills: list[str],
    config: SkillMatrixConfig,
):

    dataset_path = Path(config.dataset_path)
    dataset = (
        list(dataset_path.rglob("*.csv"))[0] if dataset_path.is_dir() else dataset_path
    )

    if not dataset.exists():
        raise FileNotFoundError(f"Dataset not found on: {dataset_path}")

    if dataset.suffix.lower() != ".csv":
        raise ValueError(f"File must be CSV: {dataset_path}")

    if config.final_output_path is None:
        raise ValueError(f"Final output path is required")

    try:
        df = pd.read_csv(dataset)
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    logger.info(f"Dataset loaded successfully from: {dataset_path}")
    builder = SkillMatrixBuilder(global_skills=list(global_skills))

    result = builder.build(df)

    save_dataframe_to_csv(result.matrix, config.final_output_path)
    logger.info(f"Processed matrix with scoring saved to: {config.final_output_path}")

    columns = ["EmployeeNumber"]
    if "JobRole" in result.matrix.columns:
        columns.append("JobRole")
    if "JobLevel" in result.matrix.columns:
        columns.append("JobLevel")
    columns += list(global_skills)

    columns = [c for c in columns if c in result.matrix.columns]
    skill_matrix = result.matrix[columns]

    save_dataframe_to_csv(skill_matrix, config.final_output_path)
    logger.info(f"Final skill matrix saved to: {config.final_output_path}")
