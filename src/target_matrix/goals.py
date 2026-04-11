from pathlib import Path

import pandas as pd

from config.global_skills import GLOBAL_SKILLS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPANY_GOAL_SKILLS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "company_goal_skills.csv"
)

MAX_HIGHLIGHTED_SKILLS = 3
ESSENTIAL_THRESHOLD = 0.80
IMPORTANT_THRESHOLD = 0.50


def _discretize_company_goal_score(score: float) -> int:
    if score >= ESSENTIAL_THRESHOLD:
        return 2

    if score >= IMPORTANT_THRESHOLD:
        return 1

    return 0


def get_company_goals() -> dict[str, int]:
    goals = {skill: 0 for skill in GLOBAL_SKILLS}

    if not COMPANY_GOAL_SKILLS_PATH.exists():
        raise FileNotFoundError(
            f"Company goal skills file not found: {COMPANY_GOAL_SKILLS_PATH}"
        )

    df = pd.read_csv(COMPANY_GOAL_SKILLS_PATH)
    required_columns = {"skill", "company_goal_score"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing columns in company goal skills file: {sorted(missing_columns)}"
        )

    df = df[df["skill"].isin(GLOBAL_SKILLS)].copy()
    df = df.sort_values(
        by=["company_goal_score", "skill"],
        ascending=[False, True],
    )

    top_skills = df[df["company_goal_score"] > 0].head(MAX_HIGHLIGHTED_SKILLS)

    for _, row in top_skills.iterrows():
        skill = str(row["skill"])
        score = float(row["company_goal_score"])
        goals[skill] = _discretize_company_goal_score(score)

    return goals
