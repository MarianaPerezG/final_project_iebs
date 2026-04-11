import logging

import __main__
import pandas as pd
from pathlib import Path

from api.singleton import get_courses_api
from config.datasets import (
    COMPANY_GOAL_SKILLS_CONFIGURATION,
    COURSE_RECOMMENDATIONS_CONFIGURATION,
    DATASETS_CONFIGURATION,
    GAP_MATRIX_CONFIGURATION,
    RECOMMENDATION_MATRIX_CONFIGURATION,
    SKILL_MATRIX_CONFIGURATION,
    TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION,
    TARGET_MATRIX_CONFIGURATION,
)
from config.global_skills import GLOBAL_SKILLS
from gap_matrix.create_gap_matrix import create_gap_matrix
from recommender.create_courses_matrix import create_courses_matrix
from recommender.create_recommendation_model import generate_recommendations
from recommender.evaluate_recommendations import run_evaluation
from schemas import (
    CompanyGoalSkillsConfig,
    CourseSkillsMatrixConfig,
    DatabaseConfig,
    DownloadConfig,
    GapMatrixConfig,
    RecommendationConfig,
    SkillDemandVectorConfig,
    SkillMatrixConfig,
    TableConfig,
    TargetMatrixConfig,
)
from scripts.create_database import create_database
from scripts.download_data import download_kaggle_datasets
from skill_matrix.create_skill_matrix import create_skill_matrix
from target_matrix.create_company_goal_skills import create_company_goal_skills
from target_matrix.create_skill_demand_vector import (
    create_skill_demand_vector_by_family,
)
from target_matrix.create_target_matrix import create_target_matrix


def run_pipeline():

    try:
        testing_mode = getattr(__main__, "RECOMMENDATION_TESTING_MODE_ON", False)

        if not testing_mode:
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

            logging.info("Creating company goal skills vector")
            create_company_goal_skills(
                config=CompanyGoalSkillsConfig(
                    company_goals_path=COMPANY_GOAL_SKILLS_CONFIGURATION[
                        "COMPANY_GOALS_PATH"
                    ],
                    output_path=COMPANY_GOAL_SKILLS_CONFIGURATION["OUTPUT_PATH"],
                )
            )

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
                config=SkillDemandVectorConfig(
                    dataset_path=TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION[
                        "DATASET_PATH"
                    ],
                    mapped_output_path=TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION[
                        "MAPPED_OUTPUT_PATH"
                    ],
                    skill_demand_output_path=TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION[
                        "SKILL_DEMAND_OUTPUT_PATH"
                    ],
                )
            )

            logging.info("Creating target matrix")

            create_target_matrix(
                config=TargetMatrixConfig(
                    skill_matrix_path=TARGET_MATRIX_CONFIGURATION["SKILL_MATRIX_PATH"],
                    skill_demand_path=TARGET_MATRIX_CONFIGURATION["SKILL_DEMAND_PATH"],
                    final_output_path=TARGET_MATRIX_CONFIGURATION[
                        "FINAL_TARGET_MATRIX_OUTPUT_PATH"
                    ],
                )
            )

            logging.info("Creating gap matrix")

            create_gap_matrix(
                config=GapMatrixConfig(
                    skill_matrix_path=GAP_MATRIX_CONFIGURATION["SKILL_MATRIX_PATH"],
                    target_matrix_path=GAP_MATRIX_CONFIGURATION["TARGET_MATRIX_PATH"],
                    final_output_path=GAP_MATRIX_CONFIGURATION[
                        "FINAL_GAP_MATRIX_OUTPUT_PATH"
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
                        TableConfig(
                            name="gap_matrix",
                            csv_path=COURSE_RECOMMENDATIONS_CONFIGURATION[
                                "GAP_MATRIX_PATH"
                            ],
                        ),
                        TableConfig(
                            name="employees",
                            sql_schema="""
                                CREATE TABLE employees (
                                    id TEXT PRIMARY KEY,
                                    job_role TEXT NOT NULL,
                                    job_level INTEGER NOT NULL,
                                    education INTEGER NOT NULL,
                                    performance INTEGER NOT NULL,
                                    current_skills TEXT NOT NULL,
                                    target_skills TEXT NOT NULL,
                                    gap_skills TEXT NOT NULL,
                                    recommendations TEXT NOT NULL,
                                    created_at TEXT NOT NULL
                                )
                            """,
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
                recommendations_output_path=COURSE_RECOMMENDATIONS_CONFIGURATION[
                    "CURRENT_EMPLOYEES_RECOMMENDATIONS_PATH"
                ],
                top_k=3,
            )
        )

        run_evaluation(
            config=RecommendationConfig(
                gap_matrix_path=COURSE_RECOMMENDATIONS_CONFIGURATION["GAP_MATRIX_PATH"],
                course_matrix_path=COURSE_RECOMMENDATIONS_CONFIGURATION[
                    "COURSE_MATRIX_PATH"
                ],
                model_output_path=COURSE_RECOMMENDATIONS_CONFIGURATION["MODEL_PATH"],
                recommendations_output_path=COURSE_RECOMMENDATIONS_CONFIGURATION[
                    "CURRENT_EMPLOYEES_RECOMMENDATIONS_PATH"
                ],
                top_k=3,
            )
        )

        logging.info("Pipeline executed successfully")
    except Exception as e:
        logging.error(f"Error occurred while running pipeline: {e}")
        raise


def recalculate_pipeline_from_new_company_goal():
    try:
        logging.info("Starting pipeline recalculation from new company goals")

        skill_matrix_path = Path(
            SKILL_MATRIX_CONFIGURATION["FINAL_SKILL_MATRIX_OUTPUT_PATH"]
        )
        skill_demand_path = Path(
            TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION["SKILL_DEMAND_OUTPUT_PATH"]
        )

        if not skill_matrix_path.exists():
            raise FileNotFoundError(
                f"Skill matrix not found. Please run the full pipeline first at: {skill_matrix_path}"
            )

        if not skill_demand_path.exists():
            raise FileNotFoundError(
                f"Skill demand vector not found. Please run the full pipeline first at: {skill_demand_path}"
            )

        try:
            skill_demand_df = pd.read_csv(skill_demand_path)
            if skill_demand_df.empty:
                raise ValueError("Skill demand vector file is empty")
            if (
                "skill" not in skill_demand_df.columns
                or "demand_score" not in skill_demand_df.columns
            ):
                raise ValueError(
                    f"Skill demand vector missing required columns. Found: {skill_demand_df.columns.tolist()}"
                )
        except pd.errors.EmptyDataError:
            raise ValueError("Skill demand vector file is empty or corrupted")

        logging.info("Prerequisites validated")

        logging.info("Creating company goal skills")
        create_company_goal_skills(
            config=CompanyGoalSkillsConfig(
                company_goals_path=COMPANY_GOAL_SKILLS_CONFIGURATION[
                    "COMPANY_GOALS_PATH"
                ],
                output_path=COMPANY_GOAL_SKILLS_CONFIGURATION["OUTPUT_PATH"],
            )
        )

        logging.info("Creating target matrix")
        create_target_matrix(
            config=TargetMatrixConfig(
                skill_matrix_path=SKILL_MATRIX_CONFIGURATION[
                    "FINAL_SKILL_MATRIX_OUTPUT_PATH"
                ],
                skill_demand_path=TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION[
                    "SKILL_DEMAND_OUTPUT_PATH"
                ],
                final_output_path=TARGET_MATRIX_CONFIGURATION[
                    "FINAL_TARGET_MATRIX_OUTPUT_PATH"
                ],
            )
        )

        logging.info("Creating gap matrix")
        create_gap_matrix(
            config=GapMatrixConfig(
                skill_matrix_path=GAP_MATRIX_CONFIGURATION["SKILL_MATRIX_PATH"],
                target_matrix_path=GAP_MATRIX_CONFIGURATION["TARGET_MATRIX_PATH"],
                final_output_path=GAP_MATRIX_CONFIGURATION[
                    "FINAL_GAP_MATRIX_OUTPUT_PATH"
                ],
            )
        )

        logging.info("Generating recommendations")
        generate_recommendations(
            config=RecommendationConfig(
                gap_matrix_path=COURSE_RECOMMENDATIONS_CONFIGURATION["GAP_MATRIX_PATH"],
                course_matrix_path=COURSE_RECOMMENDATIONS_CONFIGURATION[
                    "COURSE_MATRIX_PATH"
                ],
                model_output_path=COURSE_RECOMMENDATIONS_CONFIGURATION["MODEL_PATH"],
                recommendations_output_path=COURSE_RECOMMENDATIONS_CONFIGURATION[
                    "CURRENT_EMPLOYEES_RECOMMENDATIONS_PATH"
                ],
                top_k=3,
            )
        )

        logging.info("Pipeline recalculation completed successfully")

    except Exception as e:
        logging.error(f"Error during pipeline recalculation: {e}", exc_info=True)
        raise
