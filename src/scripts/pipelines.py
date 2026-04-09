import logging

from api.singleton import get_courses_api
from config.datasets import (
    COURSE_RECOMMENDATIONS_CONFIGURATION,
    DATASETS_CONFIGURATION,
    RECOMMENDATION_MATRIX_CONFIGURATION,
    SKILL_MATRIX_CONFIGURATION,
    TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION,
    TARGET_MATRIX_CONFIGURATION,
)
from config.global_skills import GLOBAL_SKILLS
from recommender.create_courses_matrix import create_courses_matrix
from recommender.create_recommendation_model import generate_recommendations
from schemas import (
    CourseSkillsMatrixConfig,
    DatabaseConfig,
    DownloadConfig,
    RecommendationConfig,
    SkillDemandConfig,
    SkillMatrixConfig,
    TableConfig,
    TargetMatrixConfig,
)
from scripts.create_database import create_database
from scripts.download_data import download_kaggle_datasets
from skill_matrix.create_skill_matrix import create_skill_matrix
from target_matrix.create_skill_demand_vector import (
    create_skill_demand_vector_by_family,
)
from target_matrix.create_target_matrix import create_target_matrix


def run_pipeline():

    try:
        logging.info("Starting dataset download")

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

        logging.info("Dataset download completed. Creating skill matrix")

        create_skill_matrix(
            global_skills=GLOBAL_SKILLS,
            config=SkillMatrixConfig(
                dataset_path=SKILL_MATRIX_CONFIGURATION["DATASET_PATH"],
                final_output_path=SKILL_MATRIX_CONFIGURATION[
                    "FINAL_SKILL_MATRIX_OUTPUT_PATH"
                ],
            ),
        )

        logging.info("Creating skill demand vector")

        create_skill_demand_vector_by_family(
            config=SkillDemandConfig(
                dataset_path=TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION["DATASET_PATH"],
                mapped_output_path=TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION[
                    "MAPPED_OUTPUT_PATH"
                ],
                skill_demand_output_path=TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION[
                    "SKILL_DEMAND_OUTPUT_PATH"
                ],
            )
        )

        create_target_matrix(
            config=TargetMatrixConfig(
                skill_matrix_path=TARGET_MATRIX_CONFIGURATION["SKILL_MATRIX_PATH"],
                skill_demand_path=TARGET_MATRIX_CONFIGURATION["SKILL_DEMAND_PATH"],
                final_output_path=TARGET_MATRIX_CONFIGURATION[
                    "FINAL_TARGET_MATRIX_OUTPUT_PATH"
                ],
            )
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

        logging.info("Database created successfully")

        logging.info("Fetching courses from API...")
        api = get_courses_api()
        courses = api.get_courses()
        logging.info(f"Retrieved {len(courses.courses)} courses from API")

        create_courses_matrix(
            config=CourseSkillsMatrixConfig(
                courses_response=courses,
                output_path=RECOMMENDATION_MATRIX_CONFIGURATION[
                    "FINAL_RECOMMENDATION_MATRIX_OUTPUT_PATH"
                ],
                report_path=RECOMMENDATION_MATRIX_CONFIGURATION[
                    "UNMAPPED_SKILLS_REPORT_PATH"
                ],
                mapping_threshold=0.75,
            )
        )

        logging.info("Generating course recommendations...")

        generate_recommendations(
            config=RecommendationConfig(
                gap_matrix_path=COURSE_RECOMMENDATIONS_CONFIGURATION["GAP_MATRIX_PATH"],
                course_matrix_path=COURSE_RECOMMENDATIONS_CONFIGURATION[
                    "COURSE_MATRIX_PATH"
                ],
                model_output_path=COURSE_RECOMMENDATIONS_CONFIGURATION["MODEL_PATH"],
                global_skills=list(GLOBAL_SKILLS),
                recommendations_output_path=COURSE_RECOMMENDATIONS_CONFIGURATION[
                    "CURRENT_EMPLOYEES_RECOMMENDATIONS_PATH"
                ],
                topk=3,
            )
        )

        logging.info("Pipeline executed successfully")
    except Exception as e:
        logging.error(f"Error occurred while running pipeline: {e}")
        raise
