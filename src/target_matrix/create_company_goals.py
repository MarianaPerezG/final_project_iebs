import logging
import numpy as np
import pandas as pd
from pathlib import Path
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

from config.global_skills import GLOBAL_SKILLS, SKILL_DESCRIPTIONS
from scripts.save_data import save_dataframe_to_csv

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def create_company_goal_skills(
    company_goals_path: str = "data/raw/company_goals.csv",
    output_path: str | None = None,
) -> Path:
    logger.info(f"Processing company goals from {company_goals_path}")

    goals_df = pd.read_csv(company_goals_path)
    if goals_df.empty:
        raise ValueError("Company goals CSV is empty")

    goals_list = goals_df["goal"].tolist()
    logger.info(f"Loaded {len(goals_list)} company goals")

    model = _get_model()
    logger.info("Model loaded for embedding generation")

    goals_embeddings = model.encode(goals_list, convert_to_numpy=True)
    logger.info(f"Generated embeddings for {len(goals_list)} goals")

    # Generate embeddings for skill descriptions
    skill_descriptions = [
        SKILL_DESCRIPTIONS.get(skill, f"Expertise in {skill}")
        for skill in GLOBAL_SKILLS
    ]
    skills_embeddings = model.encode(skill_descriptions, convert_to_numpy=True)
    logger.info(f"Generated embeddings for {len(GLOBAL_SKILLS)} skills")

    similarity_matrix = np.dot(
        normalize(goals_embeddings, axis=1, norm="l2"),
        normalize(skills_embeddings, axis=1, norm="l2").T,
    )
    logger.info(f"Similarity matrix shape: {similarity_matrix.shape}")

    skill_scores = np.max(similarity_matrix, axis=0)

    min_score = np.min(skill_scores)
    max_score = np.max(skill_scores)
    if max_score > min_score:
        normalized_scores = (skill_scores - min_score) / (max_score - min_score)
    else:
        normalized_scores = np.ones_like(skill_scores) * 0.5

    logger.info(
        f"Score range after normalization: [{np.min(normalized_scores):.4f}, {np.max(normalized_scores):.4f}]"
    )

    company_goal_skills_df = pd.DataFrame(
        {
            "skill": GLOBAL_SKILLS,
            "company_goal_score": normalized_scores,
        }
    )

    destination = output_path or "data/processed/company_goal_skills.csv"
    save_path = save_dataframe_to_csv(company_goal_skills_df, destination)
    logger.info(f"Company goal skills saved to {save_path}")

    return save_path


def get_company_goal_skills_vector(
    company_goal_skills_path: str = "data/processed/company_goal_skills.csv",
) -> dict[str, float]:
    df = pd.read_csv(company_goal_skills_path)
    return dict(zip(df["skill"], df["company_goal_score"]))
