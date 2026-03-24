from pathlib import Path

from data.configuration.datasets import DATASETS_CONFIGURATION, SKILL_MATRIX_CONFIGURATION
from schemas import DownloadConfig, SkillMatrixConfig
from scripts.download_data import download_kaggle_dataset


def create_skill_matrix_config():
        
    return SkillMatrixConfig(
        dataset_path=SKILL_MATRIX_CONFIGURATION["DATASET_PATH"],
        output_path=SKILL_MATRIX_CONFIGURATION["OUTPUT_PATH"]
    )
