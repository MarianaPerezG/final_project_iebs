import logging

from config.datasets import DATASETS_CONFIGURATION, SKILL_MATRIX_CONFIGURATION
from config.global_skills import GLOBAL_SKILLS
from schemas import DatabaseConfig, DownloadConfig, SkillMatrixConfig, TableConfig
from api.singleton import get_job_api

import pandas as pd

from scripts.create_skill_matrix import create_skill_matrix
from scripts.download_data import download_kaggle_datasets
from scripts.create_database import create_database


def run_pipeline():

    try:
        logging.info("Starting dataset download...")
        download_kaggle_datasets(
            [
                DownloadConfig(
                    dataset_ref=DATASETS_CONFIGURATION["SKILL_MATRIX_DATASET_REF"],
                    output_path=DATASETS_CONFIGURATION["SKILL_MATRIX_OUTPUT_PATH"],
                ),
                DownloadConfig(
                    dataset_ref=DATASETS_CONFIGURATION[
                        "TARGET_DEMAND_SKILL_MATRIX_DATASET_REF"
                    ],
                    output_path=DATASETS_CONFIGURATION[
                        "TARGET_DEMAND_SKILL_MATRIX_OUTPUT_PATH"
                    ],
                ),
                DownloadConfig(
                    dataset_ref=DATASETS_CONFIGURATION[
                        "COURSE_RECOMMENDATION_DATASET_REF"
                    ],
                    output_path=DATASETS_CONFIGURATION[
                        "COURSE_RECOMMENDATION_OUTPUT_PATH"
                    ],
                ),
            ]
        )

        logging.info("Dataset download completed. Creating skill matrix...")

        create_skill_matrix(
            global_skills=GLOBAL_SKILLS,
            config=SkillMatrixConfig(
                dataset_path=SKILL_MATRIX_CONFIGURATION["DATASET_PATH"],
                final_output_path=SKILL_MATRIX_CONFIGURATION[
                    "FINAL_SKILL_MATRIX_OUTPUT_PATH"
                ],
            ),
        )

        create_database(
            config=DatabaseConfig(
                tables=[
                    TableConfig(
                        name="skills_matrix",
                        csv_path=SKILL_MATRIX_CONFIGURATION[
                            "FINAL_SKILL_MATRIX_OUTPUT_PATH"
                        ],
                    ),
                    TableConfig(
                        name="course_recommendation",
                        csv_path=(
                            f'{DATASETS_CONFIGURATION["COURSE_RECOMMENDATION_OUTPUT_PATH"]}/edx.csv'
                        ),
                    ),
                ],
                db_path="src/config/database.db",
            )
        )
        logging.info("Database created successfully.")

        logging.info("Fetching job postings from API...")
        api = get_job_api()
        job_postings = api.get_job_postings()
        logging.info(
            f"Retrieved {len(job_postings.job_postings)} job postings from API"
        )

        logging.info("Pipeline executed successfully.")
    except Exception as e:
        logging.error(f"Error occurred while running pipeline: {e}")
        raise
