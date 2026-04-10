import logging
import os
from pathlib import Path
from typing import List
from venv import logger

import kaggle
import pandas as pd
from dotenv import load_dotenv

from schemas import DownloadConfig

logger = logging.getLogger(__name__)


def download_kaggle_datasets(configs: list[DownloadConfig]):

    load_dotenv()
    if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
        raise ValueError("Kaggle credentials not found in .env")

    api = kaggle.api
    api.authenticate()

    for config in configs:
        output_path = Path(config.output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        existing_csvs = list(output_path.rglob("*.csv"))
        if existing_csvs:
            logger.info(
                f"Dataset already exists at {existing_csvs[0]}. Skipping download."
            )
            continue

        try:
            api.dataset_download_files(
                config.dataset_ref,
                path=str(output_path),
                unzip=True,
            )

        except Exception as e:
            raise RuntimeError(f"Error downloading dataset '{config.dataset_ref}': {e}")

        logger.info(f"Dataset downloaded successfully into {output_path}")
