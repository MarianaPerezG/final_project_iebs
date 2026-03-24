from pathlib import Path
from venv import logger
import pandas as pd


def save_dataframe_to_csv(df: pd.DataFrame, output_path: str) -> Path:

    path = Path(output_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_csv(path, index=False)
    except Exception as e:
        raise ValueError(f"Error saving CSV to {path}: {e}")

    logger.info(f"CSV saved successfully at {path}")
    return path