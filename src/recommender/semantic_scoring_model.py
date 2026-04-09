from functools import lru_cache
import logging
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from config.global_skills import GLOBAL_SKILLS


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def create_course_semantic_embeddings(course_matrix: pd.DataFrame) -> np.ndarray:
    logging.info("Calculating course embeddings for semantic matching")

    course_contexts = []
    for course_idx in range(len(course_matrix)):
        course_row = course_matrix.iloc[course_idx]

        relevant_course_skills = []
        relevant_course_skills = [
            skill for skill in GLOBAL_SKILLS if float(course_row.get(skill, 0.0)) > 0.2
        ]
        course_skills_str = ", ".join(relevant_course_skills)

        course_level = str(course_row.get("level", "intermediate"))

        course_context = (
            f"Course: {course_row.get('course_title', 'Unknown')}. "
            f"Subject: {course_row.get('subject', 'General')}. "
            f"Level: {course_level}. "
            f"Teaches: {course_skills_str}. "
        )
        course_contexts.append(course_context)

    model = _get_model()

    logging.info(
        f"Course embeddings for {len(course_contexts)} courses created successfully"
    )

    return model.encode(
        course_contexts,
        convert_to_tensor=False,
        normalize_embeddings=True,
    )


def create_employee_description_embeddings(
    gap_matrix: pd.DataFrame, employee_number: int
) -> np.ndarray:
    user_row = gap_matrix[gap_matrix["EmployeeNumber"] == employee_number].iloc[0]

    gap_skills = []
    for skill in GLOBAL_SKILLS:
        gap_val = float(user_row.get(skill, 0.0))
        if gap_val > 0:
            gap_skills.append((skill, gap_val))

    gap_skills.sort(key=lambda x: x[1], reverse=True)
    top_gap_skills = [s[0] for s in gap_skills[:5]]
    gap_skills_str = ", ".join(top_gap_skills) if top_gap_skills else "general skills"

    gap_description = (
        f"Employee seeking to improve: {gap_skills_str}. "
        f"Current level: {user_row.get('JobLevel', 'unknown')}. "
        f"Needs practical training in these specific areas."
    )

    model = _get_model()

    return model.encode(
        gap_description,
        convert_to_tensor=False,
        normalize_embeddings=True,
    )
