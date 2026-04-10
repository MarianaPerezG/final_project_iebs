from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
from typing import Tuple, List, Optional
import pickle
import logging

from schemas import RecommendationConfig
from scripts.save_data import save_dataframe_to_csv
from config.levels import get_course_level_number
from recommender.semantic_scoring_model import (
    create_course_semantic_embeddings,
    create_employee_description_embeddings,
    create_employee_descriptions_batch,
)
from config.global_skills import GLOBAL_SKILLS


class CourseRecommendationModel:

    def __init__(
        self,
        gap_matrix_path: str,
        course_matrix_path: str,
        model_path: Optional[str] = None,
    ):
        self.gap_matrix_path = gap_matrix_path
        self.course_matrix_path = course_matrix_path
        self.global_skills = GLOBAL_SKILLS
        self.model_path = (
            model_path or "models/trained/course_recommendations_model.pkl"
        )

        self.gap_matrix = pd.read_csv(gap_matrix_path)
        self.course_matrix = pd.read_csv(course_matrix_path)

        if "EmployeeNumber" not in self.gap_matrix.columns:
            raise ValueError("gap_matrix must contain EmployeeNumber column")
        if "JobLevel" not in self.gap_matrix.columns:
            raise ValueError("gap_matrix must contain JobLevel column")
        if "course_title" not in self.course_matrix.columns:
            raise ValueError("course_matrix must contain course_title column")

    def save(self):
        model_path_obj = Path(self.model_path)
        model_path_obj.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "gap_matrix_path": self.gap_matrix_path,
            "course_matrix_path": self.course_matrix_path,
            "global_skills": self.global_skills,
        }

        with open(self.model_path, "wb") as f:
            pickle.dump(state, f)

        logging.info(f"Model saved to: {model_path_obj.absolute()}")

    @classmethod
    def load(cls, model_path: str):
        with open(model_path, "rb") as f:
            state = pickle.load(f)

        model = cls(
            gap_matrix_path=state["gap_matrix_path"],
            course_matrix_path=state["course_matrix_path"],
            global_skills=state["global_skills"],
            model_path=model_path,
        )
        logging.info(f"Model loaded from: {model_path}")
        return model


class CourseRecommender:
    def __init__(self, model: CourseRecommendationModel):
        self.model = model
        self.gap_matrix = model.gap_matrix
        self.course_matrix = model.course_matrix
        self.global_skills = model.global_skills

        logging.info("Creatingcourse embeddings and vectors")
        self._course_embeddings = create_course_semantic_embeddings(self.course_matrix)

        self._course_matrix_values = np.array(
            [
                normalize(
                    np.array(
                        [float(row.get(skill, 0.0)) for skill in self.global_skills]
                    ).reshape(1, -1),
                    axis=1,
                    norm="l2",
                ).ravel()
                for _, row in self.course_matrix.iterrows()
            ]
        )

        self._course_levels = np.array(
            [
                get_course_level_number(str(row.get("level", "intermediate")))
                for _, row in self.course_matrix.iterrows()
            ]
        )

        logging.info(
            f"Created: {len(self._course_embeddings)} course embeddings, {self._course_matrix_values.shape} skill vectors"
        )

    def _level_compatibility_factor(self, course_level: str, job_level: int) -> float:
        course_lvl_num = get_course_level_number(course_level)
        diff = abs(course_lvl_num - job_level)

        if diff == 0:
            factor = 1.0
        elif diff == 1:
            factor = 0.8
        elif diff == 2:
            factor = 0.4
        else:  # diff >= 3
            factor = 0.05

        return factor

    def _get_user_gap_vector(self, employee_number: int) -> Tuple[np.ndarray, int]:

        user_row = self.gap_matrix[self.gap_matrix["EmployeeNumber"] == employee_number]

        if user_row.empty:
            raise ValueError(f"Employee {employee_number} not found in gap_matrix")

        user_row = user_row.iloc[0]
        default_job_level = 3
        job_level = int(user_row.get("JobLevel", default_job_level))

        gap_vector = np.array(
            [float(user_row.get(skill, 0.0)) for skill in self.global_skills]
        )

        gap_norm = normalize(gap_vector.reshape(1, -1), axis=1, norm="l2").ravel()

        return gap_norm, job_level

    def _get_course_vector(self, course_idx: int) -> Tuple[np.ndarray, str]:
        course_row = self.course_matrix.iloc[course_idx]
        course_level = str(course_row.get("level", "intermediate"))

        course_vector = np.array(
            [float(course_row.get(skill, 0.0)) for skill in self.global_skills]
        )

        course_norm = normalize(course_vector.reshape(1, -1), axis=1, norm="l2").ravel()

        return course_norm, course_level

    def generate_recommendations_for_employee(
        self, employee_number: int, topk: int = 3
    ) -> List[dict]:
        gap_vec, job_level = self._get_user_gap_vector(employee_number)

        employee_embedding = create_employee_description_embeddings(
            self.gap_matrix, employee_number
        )

        recommendations = []

        for course_idx in range(len(self.course_matrix)):
            course_row = self.course_matrix.iloc[course_idx]

            skill_cols = [c for c in self.global_skills if c in course_row.index]
            total_score = sum(float(course_row.get(c, 0.0)) for c in skill_cols)
            if total_score == 0:
                continue

            course_vec = self._course_matrix_values[course_idx]
            course_level = str(
                self.course_matrix.iloc[course_idx].get("level", "intermediate")
            )

            # HARD FILTER: Only include courses within ±1 level
            course_lvl_num = get_course_level_number(course_level)
            level_diff = abs(course_lvl_num - job_level)
            if level_diff > 2:
                continue

            # Numeric similarity (original cosine)
            cosine_sim = np.dot(gap_vec, course_vec)

            # Level compatibility
            level_factor = self._level_compatibility_factor(course_level, job_level)

            # Semantic similarity - just dot product, employee already encoded
            course_embedding = self._course_embeddings[course_idx]
            semantic_sim = float(np.dot(employee_embedding, course_embedding))
            semantic_sim = max(0.0, min(1.0, semantic_sim))

            final_score = 0.2 * cosine_sim + 0.3 * semantic_sim + 0.5 * level_factor

            recommendations.append(
                {
                    "employee_number": employee_number,
                    "course_title": course_row.get("course_title", ""),
                    "course_level": course_level,
                    "course_subject": course_row.get("subject", ""),
                    "cosine_similarity": round(cosine_sim, 4),
                    "semantic_similarity": round(semantic_sim, 4),
                    "level_factor": round(level_factor, 4),
                    "final_score": round(final_score, 4),
                }
            )

        recommendations.sort(key=lambda x: x["final_score"], reverse=True)
        return recommendations[:topk]

    def generate_recommendations_for_all_employees(self, topk: int = 3) -> pd.DataFrame:
        """
        Vectorized batch generation for all employees using pre-cached course data.
        Much faster than calling generate_recommendations_for_employee per employee.
        """
        logging.info(
            "Generating recommendations using cached course vectors and embeddings..."
        )

        gap_matrix_values = np.array(
            [
                normalize(
                    np.array(
                        [float(row.get(skill, 0.0)) for skill in self.global_skills]
                    ).reshape(1, -1),
                    axis=1,
                    norm="l2",
                ).ravel()
                for _, row in self.gap_matrix.iterrows()
            ]
        )

        employee_numbers = self.gap_matrix["EmployeeNumber"].values
        employee_levels = self.gap_matrix["JobLevel"].values

        course_matrix_values = self._course_matrix_values
        course_levels = self._course_levels

        cosine_similarities = gap_matrix_values @ course_matrix_values.T

        # Use BATCH encoding: encode all 282 employees in ONE model.encode() call
        employee_embeddings = create_employee_descriptions_batch(
            self.gap_matrix
        )  # Shape: (282, 384)

        semantic_similarities = np.dot(employee_embeddings, self._course_embeddings.T)
        semantic_similarities = np.clip(semantic_similarities, 0.0, 1.0)

        level_diffs = np.abs(
            employee_levels.reshape(-1, 1) - course_levels.reshape(1, -1)
        )
        level_factors = np.where(
            level_diffs == 0,
            1.0,
            np.where(
                level_diffs == 1,
                0.8,
                np.where(level_diffs == 2, 0.4, 0.05),  # diff >= 3
            ),
        )

        # HARD FILTER: Mask courses outside ±2 level range for balanced coverage & compatibility
        level_mask = level_diffs <= 2
        final_scores = (
            0.2 * cosine_similarities
            + 0.3 * semantic_similarities
            + 0.5 * level_factors
        )
        # Set scores to -inf for out-of-range courses so they're never selected in top-k
        final_scores[~level_mask] = -np.inf

        all_recommendations = []

        for emp_idx, emp_num in enumerate(employee_numbers):
            employee_scores = final_scores[emp_idx]
            topk_indices = np.argsort(employee_scores)[-topk:][::-1]  # Descending order

            for rank_idx, course_idx in enumerate(topk_indices, 1):
                if employee_scores[course_idx] > 0:  # Only include non-zero scores
                    course_row = self.course_matrix.iloc[course_idx]

                    all_recommendations.append(
                        {
                            "employee_number": int(emp_num),
                            "rank": rank_idx,
                            "course_title": course_row.get("course_title", ""),
                            "course_level": course_row.get("level", "intermediate"),
                            "course_subject": course_row.get("subject", ""),
                            "cosine_similarity": round(
                                float(cosine_similarities[emp_idx, course_idx]), 4
                            ),
                            "semantic_similarity": round(
                                float(semantic_similarities[emp_idx, course_idx]), 4
                            ),
                            "level_factor": round(
                                float(level_factors[emp_idx, course_idx]), 4
                            ),
                            "final_score": round(float(employee_scores[course_idx]), 4),
                        }
                    )

        logging.info(
            f"Generated {len(all_recommendations)} recommendations via cached vectorization"
        )
        return pd.DataFrame(all_recommendations)


def _train_and_save_model(config: RecommendationConfig) -> CourseRecommendationModel:
    logging.info("Training recommendation model")

    model = CourseRecommendationModel(
        gap_matrix_path=config.gap_matrix_path,
        course_matrix_path=config.course_matrix_path,
        model_path=config.model_output_path,
    )

    model.save()
    logging.info("Model training and saving complete.")
    return model


def generate_recommendations(config: RecommendationConfig):
    logging.info("Initializing course recommendation pipeline")

    model = _train_and_save_model(config)

    recommender = CourseRecommender(model)

    logging.info("Generating recommendations for all employees")
    recommendations_df = recommender.generate_recommendations_for_all_employees(
        topk=config.top_k
    )

    if recommendations_df.empty:
        logging.warning("No recommendations generated.")
        return

    logging.info(f"Generated {len(recommendations_df)} recommendations")

    output_path = Path(config.recommendations_output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    save_dataframe_to_csv(recommendations_df, str(output_path))
    logging.info(
        f"Recommendations for current employees saved to: {output_path.absolute()}"
    )
