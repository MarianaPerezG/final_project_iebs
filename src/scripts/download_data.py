from pathlib import Path

from dotenv import load_dotenv
import kaggle
import pandas as pd
import os


def download_kaggle_dataset(dataset_ref: str,output_dir: str = "src/data/raw"):
  
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    load_dotenv()
    if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
        raise ValueError("Kaggle credentials not found in .env")
    
    api = kaggle.api
    api.authenticate()
    
    try:
        api.dataset_download_files(
            dataset_ref,
            path=str(output_path),
            unzip=True
        )
    except Exception as e:
        raise RuntimeError(f"Error downloading dataset: {e}")

    print(f"Dataset downloaded successfully into {output_path}")


DATASET_REF = "marianaprezgonzlez/ibm-hr-analytics-employee-attrition-and-performance"
download_kaggle_dataset(DATASET_REF)