from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


def save_dataframe_to_csv(df: pd.DataFrame, output_path: str) -> Path:

    path = Path(output_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_csv(path, index=False)
    except Exception as e:
        raise ValueError(f"Error saving CSV to {path}: {e}")

    logger.info(f"CSV saved successfully at {path}")

    logger.info(f"First row of the DataFrame: {df.head(1).iloc[0].to_dict()}")
    return path
