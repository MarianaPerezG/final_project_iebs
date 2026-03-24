from pathlib import Path

from data.configuration.datasets import DATASETS_CONFIGURATION, SKILL_MATRIX_CONFIGURATION
from schemas import DownloadConfig, SkillMatrixConfig
from scripts.download_data import download_kaggle_dataset


def create_skill_matrixconfig():
    
    download_dataset_if_needed()
        
    return SkillMatrixConfig(
        dataset_path=SKILL_MATRIX_CONFIGURATION["DATASET_PATH"],
        output_path=SKILL_MATRIX_CONFIGURATION["OUTPUT_PATH"]
    )
    

    
def download_dataset_if_needed():
    dataset_path = Path(DATASETS_CONFIGURATION["SIKLL_MATRIX_OUTPUT_PATH"])
    
    if not dataset_path.exists():   
        download_kaggle_dataset(DownloadConfig(
            dataset_ref=DATASETS_CONFIGURATION["SKILL_MATRIX_DATASET_REF"],
            output_path=DATASETS_CONFIGURATION["SIKLL_MATRIX_OUTPUT_PATH"]
        ))
    else:
        print(f"Dataset already exists at {dataset_path}, skipping download.")