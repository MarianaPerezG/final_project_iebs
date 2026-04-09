from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from scripts.save_data import save_dataframe_to_csv


def create_company_goals(goals: list[str], output_path: str | None = None) -> Path:
    """Create a raw CSV file with company goals."""
    cleaned_goals = [goal.strip() for goal in goals if goal and goal.strip()]
    if not cleaned_goals:
        raise ValueError("At least one company goal is required.")

    timestamp = datetime.now(timezone.utc).isoformat()
    goals_df = pd.DataFrame(
        {
            "goal_id": range(1, len(cleaned_goals) + 1),
            "goal": cleaned_goals,
            "created_at": [timestamp] * len(cleaned_goals),
        }
    )

    destination = output_path or "data/raw/company_goals.csv"
    return save_dataframe_to_csv(goals_df, destination)
