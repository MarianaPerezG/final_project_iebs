"""Calculate target skills for a specific job role."""

from pathlib import Path
from typing import Dict
import pandas as pd
import logging
import sys

src_path = Path(__file__).parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from config.global_skills import GLOBAL_SKILLS
from config.scoring_rules import FAMILY_SCORES, ROLE_TO_FAMILY
from config.datasets import (
    TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION,
    COMPANY_GOAL_SKILLS_CONFIGURATION,
)

logger = logging.getLogger(__name__)


def calculate_target_skills_for_role(
    job_role: str, alpha: float = 0.30, beta: float = 0.50
) -> Dict[str, float]:
    try:
        if job_role not in ROLE_TO_FAMILY:
            raise ValueError(f"Unknown job role: {job_role}")

        family = ROLE_TO_FAMILY[job_role]
        base_scores = FAMILY_SCORES[family]

        skill_demand_path = TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION.get(
            "SKILL_DEMAND_OUTPUT_PATH"
        )

        demand_by_skill = {}
        if skill_demand_path and Path(skill_demand_path).exists():
            try:
                skill_demand_df = pd.read_csv(skill_demand_path)
                demand_by_skill = {
                    row["skill"]: float(row["demand_score"])
                    for _, row in skill_demand_df.iterrows()
                }
            except Exception as e:
                logger.warning(f"Could not load skill demand: {e}")

        goals_by_skill = {}
        goals_path = COMPANY_GOAL_SKILLS_CONFIGURATION.get("OUTPUT_PATH")

        if goals_path and Path(goals_path).exists():
            try:
                goals_df = pd.read_csv(goals_path)
                if not goals_df.empty:
                    goals_by_skill = {
                        col: int(goals_df[col].sum())
                        for col in GLOBAL_SKILLS
                        if col in goals_df.columns
                    }
            except Exception as e:
                logger.warning(f"Could not load company goals: {e}")

        target_skills = {}
        for skill in GLOBAL_SKILLS:
            base_value = float(base_scores.get(skill, 0))
            demand_score = demand_by_skill.get(skill, 0.0)
            goal_value = goals_by_skill.get(skill, 0)

            # Formula: base * (1 + alpha * demand) + beta * goals
            target_value = base_value * (1 + alpha * demand_score) + beta * goal_value
            target_value = max(0.0, min(5.0, target_value))  # Clamp to [0.0, 5.0]

            target_skills[skill] = round(target_value, 3)

        logger.info(f"Calculated target skills for role: {job_role}")
        return target_skills

    except Exception as e:
        logger.error(f"Error calculating target skills for role {job_role}: {e}")
        raise
