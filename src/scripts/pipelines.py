import logging

import data.configuration.datasets
from data.global_skills import GLOBAL_SKILLS
from schemas import DownloadConfig

import pandas as pd

from scripts.create_skill_matrix import create_skill_matrix
from scripts.download_data import download_kaggle_dataset
from skill_matrix.configuration import create_skill_matrix_config


def run_pipeline():
    
    try:
        logging.info("Starting dataset download...")
        download_kaggle_dataset(DownloadConfig(
            dataset_ref=data.configuration.datasets.DATASETS_CONFIGURATION["SKILL_MATRIX_DATASET_REF"],
            output_path=data.configuration.datasets.DATASETS_CONFIGURATION["SKILL_MATRIX_OUTPUT_PATH"]
        ))
        logging.info("Dataset download completed. Creating skill matrix...")
        create_skill_matrix(
            global_skills=GLOBAL_SKILLS, 
            config= create_skill_matrix_config()
        )
        logging.info("Pipeline executed successfully.")
    except Exception as e:
        logging.error(f"Error occurred while running pipeline: {e}")
        raise