from pathlib import Path

from dotenv import load_dotenv
import kaggle
import pandas as pd
import os

from schemas import DownloadConfig


def download_kaggle_dataset(config: DownloadConfig):
  
    output_path = Path(config.output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    load_dotenv()
    if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
        raise ValueError("Kaggle credentials not found in .env")
    
    api = kaggle.api
    api.authenticate()
    
    try:
        api.dataset_download_files(
            config.dataset_ref,
            path=str(output_path),
            unzip=True
        )
    except Exception as e:
        raise RuntimeError(f"Error downloading dataset: {e}")


    print(f"Dataset downloaded successfully into {output_path}")

