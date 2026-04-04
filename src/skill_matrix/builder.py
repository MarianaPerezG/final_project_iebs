from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import pandas as pd

from schemas import MatrixBuildResult
from skill_matrix import scoring


@dataclass
class SkillMatrixBuilder:
    global_skills: List[str]

    def build(self, df: pd.DataFrame) -> MatrixBuildResult:

        for skill in self.global_skills:
            if skill not in df.columns:
                df[skill] = pd.NA

        matrix = df.copy()

        if "JobRole" in df.columns:
            scores = matrix.apply(
                lambda row: scoring.score_employee(
                    row["JobRole"],
                    int(row["Education"]),
                    int(row["PerformanceRating"]),
                ),
                axis=1,
            )
            scores_df = pd.DataFrame(scores.tolist(), index=matrix.index)
            matrix[self.global_skills] = scores_df[self.global_skills]
        else:
            raise ValueError("JobRole column is required for scoring")

        metadata = {
            "n_rows": len(matrix),
            "n_skills": len(matrix.columns),
            "skills": list(matrix.columns),
        }

        return MatrixBuildResult(matrix=matrix, metadata=metadata)
