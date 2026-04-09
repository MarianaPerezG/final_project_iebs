from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd

from config.scoring_rules import FAMILY_SCORES, ROLE_TO_FAMILY
from schemas import MatrixBuildResult


@dataclass
class TargetMatrixBuilder:
    global_skills: List[str]
    alpha: float = 0.30
    beta: float = 0.50

    def build_from_family(
        self,
        skill_matrix_df: pd.DataFrame,
        skill_demand_df: pd.DataFrame,
        company_goals: dict[str, int],
    ) -> MatrixBuildResult:
        self._validate_skill_matrix(skill_matrix_df)
        self._validate_skill_demand(skill_demand_df)

        demand_by_skill = self._build_demand_by_skill(skill_demand_df)
        goals_by_skill = {
            skill: int(company_goals.get(skill, 0)) for skill in self.global_skills
        }

        matrix = skill_matrix_df.copy()
        matrix["family"] = matrix["JobRole"].map(ROLE_TO_FAMILY)

        if matrix["family"].isna().any():
            missing_roles = sorted(
                matrix.loc[matrix["family"].isna(), "JobRole"]
                .dropna()
                .unique()
                .tolist()
            )
            raise ValueError(f"unmapped job roles: {missing_roles}")

        for skill in self.global_skills:
            base_values = matrix["family"].map(
                lambda family: float(FAMILY_SCORES[family].get(skill, 0))
            )

            demand_score = demand_by_skill.get(skill, 0.0)
            goal_value = goals_by_skill.get(skill, 0)

            target_values = (
                base_values * (1 + self.alpha * demand_score) + self.beta * goal_value
            ).clip(lower=0.0, upper=5.0)

            matrix[skill] = target_values.round(3)

        columns = ["EmployeeNumber", "JobRole", "family", *self.global_skills]
        columns = [column for column in columns if column in matrix.columns]
        matrix = matrix[columns].copy()

        return MatrixBuildResult(
            matrix=matrix,
            metadata={
                "n_rows": len(matrix),
                "n_skills": len(self.global_skills),
                "alpha": self.alpha,
                "beta": self.beta,
            },
            applied_transformers=[
                "role_to_family_mapping",
                "base_family_projection",
                "skill_demand_adjustment",
                "company_goals_adjustment",
            ],
        )

    def _build_demand_by_skill(self, skill_demand_df: pd.DataFrame) -> dict[str, float]:
        demand_by_skill = skill_demand_df.groupby("skill", as_index=False).agg(
            demand_score=("demand_score", "max")
        )

        return {
            row["skill"]: float(row["demand_score"])
            for _, row in demand_by_skill.iterrows()
        }

    @staticmethod
    def _validate_skill_matrix(df: pd.DataFrame) -> None:
        required_columns = {"JobRole"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"missing columns in skill matrix: {sorted(missing_columns)}"
            )

    @staticmethod
    def _validate_skill_demand(df: pd.DataFrame) -> None:
        required_columns = {"skill", "demand_score"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"missing columns in skill demand: {sorted(missing_columns)}"
            )
