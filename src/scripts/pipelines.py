from data.configuration.datasets import DATASETS_CONFIGURATION, SKILL_MATRIX_CONFIGURATION
from data.global_skills import GLOBAL_SKILLS
from schemas import DownloadConfig

import pandas as pd

from scripts.create_skill_matrix import create_skill_matrix
from scripts.download_data import download_kaggle_dataset
from skill_matrix.configuration import create_skill_matrix_config


def run_pipeline():
    
    download_kaggle_dataset(DownloadConfig(
        dataset_ref=DATASETS_CONFIGURATION["SKILL_MATRIX_DATASET_REF"],
        output_path=DATASETS_CONFIGURATION["SKILL_MATRIX_OUTPUT_PATH"]
    ))
    
    
    create_skill_matrix(
        global_skills=GLOBAL_SKILLS, 
        config= create_skill_matrix_config()
    )


