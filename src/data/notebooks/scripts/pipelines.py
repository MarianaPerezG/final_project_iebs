from pathlib import Path
from skill_matrix.builder import SkillMatrixBuilder

import pandas as pd

def run_pipeline(
    dataset_path: str,
    output_path: str,
    global_skills: list[str],
    transformers: list | None = None,
):
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found on: {dataset_path}")
    
    if dataset_path.suffix.lower() != ".csv":
        raise ValueError(f"File must be CSV: {dataset_path}")
    
    if output_path is None:
        raise ValueError(f"Output_path is required")
    
    try:
        df = pd.read_csv(dataset_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    builder = SkillMatrixBuilder(
        global_skills=list(global_skills),
        transformers=[]
    )

    result = builder.build(df)

    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.matrix.to_csv(output_path, index=False)
    except Exception as e:
        raise ValueError(f"Error generating output CSV: {e}")

    return print(f"SkillMatrix created in {output_path}")