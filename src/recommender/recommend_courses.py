import logging
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
from typing import Tuple, List, Optional, Dict
import pickle

from schemas import RecommendationConfig
from scripts.save_data import save_dataframe_to_csv


class CourseRecommendationModel:

    def __init__(
        self,
        gap_matrix_path: str,
        course_matrix_path: str,
        global_skills: List[str],
        model_path: Optional[str] = None,
    ):
        self.gap_matrix_path = gap_matrix_path
        self.course_matrix_path = course_matrix_path
        self.global_skills = global_skills
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
        """Load model from disk."""
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
        """
        Initialize recommender with a trained model.

        Parameters:
        -----------
        model : CourseRecommendationModel
            Loaded or created recommendation model
        """
        self.model = model
        self.gap_matrix = model.gap_matrix
        self.course_matrix = model.course_matrix
        self.global_skills = model.global_skills

    def _level_compatibility_factor(self, course_level: str, job_level: int) -> float:
        level_map = {
            "beginner": 1,
            "intermediate-beginner": 2,
            "intermediate": 3,
            "intermediate-advanced": 4,
            "advanced": 5,
        }

        course_lvl_num = level_map.get(str(course_level).lower(), 3)

        diff = abs(course_lvl_num - job_level)

        # Factor: perfect match = 1.0, penalize distance
        # allow up to ±1 level with minimal penalty, then drop faster
        if diff <= 1:
            factor = 1.0 - (diff * 0.1)  # 1.0 or 0.9
        else:
            factor = max(0.3, 1.0 - (diff * 0.25))  # drop to min 0.3

        return factor

    def _get_user_gap_vector(self, employee_number: int) -> Tuple[np.ndarray, int]:
        """
        Extract gap vector for a user (normalized L2).

        Returns:
        --------
        Tuple of (normalized_gap_vector, job_level)
        """
        user_row = self.gap_matrix[self.gap_matrix["EmployeeNumber"] == employee_number]

        if user_row.empty:
            raise ValueError(f"Employee {employee_number} not found in gap_matrix")

        user_row = user_row.iloc[0]
        job_level = int(user_row.get("JobLevel", 3))

        # Extract gap values for each skill
        gap_vector = np.array(
            [float(user_row.get(skill, 0.0)) for skill in self.global_skills]
        )

        # Normalize (L2)
        gap_norm = normalize(gap_vector.reshape(1, -1), axis=1, norm="l2").ravel()

        return gap_norm, job_level

    def _get_course_vector(self, course_idx: int) -> Tuple[np.ndarray, str]:
        """
        Extract skill vector for a course (normalized L2).

        Returns:
        --------
        Tuple of (normalized_skill_vector, course_level)
        """
        course_row = self.course_matrix.iloc[course_idx]
        course_level = str(course_row.get("level", "intermediate"))

        # Extract skill scores for each global skill
        course_vector = np.array(
            [float(course_row.get(skill, 0.0)) for skill in self.global_skills]
        )

        # Normalize (L2)
        course_norm = normalize(course_vector.reshape(1, -1), axis=1, norm="l2").ravel()

        return course_norm, course_level

    def recommend(self, employee_number: int, topk: int = 3) -> List[dict]:
        gap_vec, job_level = self._get_user_gap_vector(employee_number)

        recommendations = []

        for course_idx in range(len(self.course_matrix)):
            course_row = self.course_matrix.iloc[course_idx]

            # Skip courses with no mapped skills
            skill_cols = [c for c in self.global_skills if c in course_row.index]
            total_score = sum(float(course_row.get(c, 0.0)) for c in skill_cols)
            if total_score == 0:
                continue

            # Get course vector and level
            course_vec, course_level = self._get_course_vector(course_idx)

            # Cosine similarity
            cosine_sim = np.dot(gap_vec, course_vec)

            # Apply jobLevel compatibility factor
            level_factor = self._level_compatibility_factor(course_level, job_level)

            # Final adjusted score
            final_score = cosine_sim * level_factor

            recommendations.append(
                {
                    "employee_number": employee_number,
                    "course_title": course_row.get("course_title", ""),
                    "course_level": course_level,
                    "course_subject": course_row.get("subject", ""),
                    "cosine_similarity": round(cosine_sim, 4),
                    "level_factor": round(level_factor, 4),
                    "final_score": round(final_score, 4),
                }
            )

        # Sort by final_score descending and take top-k
        recommendations.sort(key=lambda x: x["final_score"], reverse=True)
        return recommendations[:topk]

    def recommend_all(self, topk: int = 3) -> pd.DataFrame:
        all_recommendations = []

        for emp_num in self.gap_matrix["EmployeeNumber"].unique():
            try:
                recs = self.recommend(emp_num, topk=topk)
                for rank, rec in enumerate(recs, 1):
                    all_recommendations.append(
                        {
                            "employee_number": rec["employee_number"],
                            "rank": rank,
                            "course_title": rec["course_title"],
                            "course_level": rec["course_level"],
                            "course_subject": rec["course_subject"],
                            "cosine_similarity": rec["cosine_similarity"],
                            "level_factor": rec["level_factor"],
                            "final_score": rec["final_score"],
                        }
                    )
            except Exception as e:
                logging.warning(
                    f"Could not generate recommendations for employee {emp_num}: {e}"
                )
                continue

        return pd.DataFrame(all_recommendations)


def train_and_save_model(config: RecommendationConfig) -> CourseRecommendationModel:
    logging.info("Training recommendation model...")

    # Use MODEL_PATH from config if available, otherwise use output_path
    model_path = getattr(config, "model_path", None) or config.output_path

    model = CourseRecommendationModel(
        gap_matrix_path=config.gap_matrix_path,
        course_matrix_path=config.course_matrix_path,
        global_skills=config.global_skills,
        model_path=model_path,
    )

    model.save()
    logging.info("Model training and saving complete.")
    return model


def recommend_courses(config: RecommendationConfig):
    logging.info("Initializing course recommendation pipeline...")

    model = train_and_save_model(config)

    recommender = CourseRecommender(model)

    logging.info("Generating recommendations for all employees...")
    recommendations_df = recommender.recommend_all(topk=3)

    if recommendations_df.empty:
        logging.warning("No recommendations generated.")
        return

    logging.info(f"Generated {len(recommendations_df)} recommendations")

    # Save batch recommendations CSV (use separate path to not override model)
    batch_recs_path = getattr(
        config, "batch_recs_path", None
    ) or config.output_path.replace(".pkl", "_batch.csv")
    output_path = Path(batch_recs_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    save_dataframe_to_csv(recommendations_df, str(output_path))
    logging.info(f"Batch recommendations saved to: {output_path.absolute()}")

    # Optional: summary statistics
    summary = (
        recommendations_df.groupby("employee_number")
        .size()
        .reset_index(name="recommendations_count")
    )
    logging.info(
        f"Average recommendations per employee: {summary['recommendations_count'].mean():.1f}"
    )


def recommend_for_user(
    user_id: int, model_path: str, csv_path: Optional[str] = None, topk: int = 3
) -> List[Dict]:
    """
    Get recommendations for a specific user (hybrid mode).

    Strategy:
    1. If csv_path provided and user exists in CSV, return cached results (fast)
    2. Otherwise, load model and calculate on-the-fly (on-demand)

    Parameters:
    -----------
    user_id : int
        Employee number to recommend for
    model_path : str
        Path to saved model pickle file
    csv_path : Optional[str]
        Path to batch recommendations CSV (optional)
        If provided and user exists, returns cached results
    topk : int
        Number of recommendations to return

    Returns:
    --------
    List[Dict]
        List of recommendation dictionaries with scores

    Example:
    --------
    >>> recs = recommend_for_user(
    ...     user_id=1,
    ...     model_path="models/trained/course_recommendation_model.pkl",
    ...     csv_path="data/final/course_recommendations.csv"
    ... )
    """
    # Try cached CSV first (fast path for existing users)
    if csv_path:
        cached_recs = _get_cached_recommendations(user_id, csv_path, topk)
        if cached_recs is not None:
            logging.info(
                f"User {user_id} found in cache, returning {len(cached_recs)} recommendations"
            )
            return cached_recs
        else:
            logging.info(f"User {user_id} not in cache, calculating on-demand...")

    # Slow path: calculate on-the-fly
    model = CourseRecommendationModel.load(model_path)
    recommender = CourseRecommender(model)
    recommendations = recommender.recommend(user_id, topk=topk)

    return recommendations


def _get_cached_recommendations(
    user_id: int, csv_path: str, topk: int
) -> Optional[List[Dict]]:
    """
    Try to load recommendations from cached CSV.

    Returns None if user not found or CSV doesn't exist.
    """
    csv_path_obj = Path(csv_path)
    if not csv_path_obj.exists():
        return None

    try:
        recs_df = pd.read_csv(csv_path_obj)
        user_recs = recs_df[recs_df["employee_number"] == user_id]

        if user_recs.empty:
            return None

        # Take only top-k and convert to dict
        user_recs = user_recs.head(topk)
        recommendations = user_recs.to_dict("records")

        return recommendations
    except Exception as e:
        logging.warning(f"Failed to load cached recommendations: {e}")
        return None
