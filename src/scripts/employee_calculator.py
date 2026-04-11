import pandas as pd
from pathlib import Path
import logging
import sys
from typing import Dict, List

src_path = Path(__file__).parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config.datasets import (
    SKILL_MATRIX_CONFIGURATION,
    RECOMMENDATION_MATRIX_CONFIGURATION,
)
from config.global_skills import GLOBAL_SKILLS
from skill_matrix.scoring import score_employee
from target_matrix.role_skills import calculate_target_skills_for_role
from recommender.create_recommendation_model import (
    CourseRecommendationModel,
    CourseRecommender,
)

logger = logging.getLogger(__name__)


def calculate_employee_skills(
    job_role: str, education: int, performance: int
) -> Dict[str, str]:
    try:
        employee_skills = score_employee(job_role, education, performance)

        return employee_skills
    except Exception as e:
        logger.error(f"Error calculating employee skills: {e}")
        raise


def calculate_target_skills(job_role: str) -> Dict[str, float]:
    return calculate_target_skills_for_role(job_role)


def calculate_gap_skills(
    current_skills: Dict[str, str], target_skills: Dict[str, float]
) -> Dict[str, float]:
    gap_skills = {}
    for skill in GLOBAL_SKILLS:
        current = float(current_skills.get(skill, 0))
        target = float(target_skills.get(skill, 0))
        gap = max(0, target - current)  # Only positive gaps
        gap_skills[skill] = round(gap, 3)

    return gap_skills


def get_course_recommendations(
    job_role: str, job_level: int, gap_skills: Dict[str, float], top_k: int = 3
) -> List[Dict]:
    # Load model
    model_path = RECOMMENDATION_MATRIX_CONFIGURATION.get(
        "RECOMMENDATION_MODEL_PATH", "models/trained/course_recommendations_model.pkl"
    )

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Course recommendation model not found at {model_path}"
        )

    # Load model and recommender
    model = CourseRecommendationModel.load(model_path)
    recommender = CourseRecommender(model)

    # Use the recommender's method for employee profiles (on-the-fly embeddings)
    recommendations = recommender.generate_recommendations_for_employee_profile(
        gap_skills=gap_skills, job_level=job_level, job_role=job_role, topk=top_k
    )

    logger.info(
        f"Generated {len(recommendations)} recommendations for {job_role} (level {job_level})"
    )
    return recommendations
