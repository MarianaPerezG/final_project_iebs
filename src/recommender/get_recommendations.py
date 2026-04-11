from pathlib import Path
import pandas as pd
from typing import Optional, List, Dict
import logging

from .create_recommendation_model import CourseRecommendationModel, CourseRecommender


def get_recommendations_for_user(
    user_id: int, model_path: str, csv_path: str = None, topk: int = 3
) -> List[Dict]:

    if csv_path:
        recommendations = _get_recommendations_from_csv(user_id, csv_path, topk)
        if recommendations is not None:
            logging.info(
                f"User {user_id} found in cache, returning {len(recommendations)} recommendations"
            )
            return recommendations
        else:
            logging.info(f"User {user_id} not in cache, calculating on-demand...")

    recommendations = _recommend_for_user_with_model(user_id, model_path, topk)
    return recommendations


def _get_recommendations_from_csv(
    user_id: int, csv_path: str, topk: int
) -> Optional[List[Dict]]:

    csv_path_obj = Path(csv_path)

    if not csv_path_obj.exists():
        return None

    try:
        recs_df = pd.read_csv(csv_path_obj)
        user_recs = recs_df[recs_df["employee_number"] == user_id]

        if user_recs.empty:
            return None

        user_recs = user_recs.head(topk)
        recommendations = user_recs.to_dict("records")

        return recommendations
    except Exception as e:
        logging.warning(f"Failed to load cached recommendations: {e}")
        return None


def _recommend_for_user_with_model(
    user_id: int, model_path: str, topk: int
) -> List[Dict]:

    model = CourseRecommendationModel.load(model_path)
    recommender = CourseRecommender(model)
    recommendations = recommender.generate_recommendations_for_employee(
        user_id, topk=topk
    )
    return recommendations
