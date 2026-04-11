from pathlib import Path

import pandas as pd

from config.dummy_goals import COMPANY_GOALS as DUMMY_GOALS
from config.global_skills import GLOBAL_SKILLS


def get_company_goals() -> dict[str, int]:
    """
    Load company goals from CSV (generated via NLP) if available,
    otherwise fall back to dummy goals.

    Returns company goal scores normalized to 0-5 scale for target matrix.
    """

    """
    company_goal_skills_path = Path("data/processed/company_goal_skills.csv")

    # Try to load from generated CSV (0-1 scale from semantic analysis)
    if company_goal_skills_path.exists():
        try:
            df = pd.read_csv(company_goal_skills_path)
            # Convert 0-1 scale to 0-5 scale for consistency with target matrix
            goals_dict = {
                row["skill"]: float(row["company_goal_score"]) * 5.0
                for _, row in df.iterrows()
            }
            return {skill: float(goals_dict.get(skill, 0.0)) for skill in GLOBAL_SKILLS}
        except Exception as e:
            print(f"Warning: Could not load company_goal_skills.csv: {e}")
    """

    # Fall back to dummy goals if CSV not available
    return {skill: int(DUMMY_GOALS.get(skill, 0)) for skill in GLOBAL_SKILLS}
