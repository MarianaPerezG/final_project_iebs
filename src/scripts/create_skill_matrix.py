from pathlib import Path

import pandas as pd

from builder import MatrixBuilder
from schemas import SkillMatrixConfig
from scripts.save_data import save_dataframe_to_csv


def create_skill_matrix(
    global_skills: list[str],
    config: SkillMatrixConfig,
):

    dataset_path = Path(config.dataset_path)
    dataset = list(dataset_path.rglob("*.csv"))[0] if dataset_path.is_dir() else dataset_path

    if not dataset.exists():
        raise FileNotFoundError(f"Dataset not found on: {dataset_path}")

    if dataset.suffix.lower() != ".csv":
        raise ValueError(f"File must be CSV: {dataset_path}")

    if config.output_path is None:
        raise ValueError(f"Output_path is required")

    try:
        df = pd.read_csv(dataset)
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    builder = MatrixBuilder(global_skills=list(global_skills), transformers=[])

    result = builder.build(df)
    
    save_dataframe_to_csv(result.matrix, config.output_path)

    return result

