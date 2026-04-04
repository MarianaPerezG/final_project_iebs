from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import pandas as pd

from schemas import MatrixBuildResult
from skill_matrix.transformers.transformers import BaseMatrixTransformer
from skill_matrix import scoring


@dataclass
class SkillMatrixBuilder:
    global_skills: List[str]
    transformers: List[BaseMatrixTransformer] = field(default_factory=list)

    def build(self, df: pd.DataFrame) -> MatrixBuildResult:

        for skill in self.global_skills:
            if skill not in df.columns:
                df[skill] = pd.NA

        matrix = df.copy()

        if "JobRole" in df.columns:
            scores = matrix["JobRole"].apply(scoring.score_role)
            scores_df = pd.DataFrame(scores.tolist(), index=matrix.index)
            matrix[self.global_skills] = scores_df[self.global_skills]
        else:
            raise ValueError("JobRole column is required for scoring")

        # Si ya los scores vienen transformados, quiar los transformadores
        applied_transformers = []
        for transformer in self.transformers:
            matrix = transformer.apply(matrix, df)
            applied_transformers.append(transformer.name)

        metadata = {
            "n_rows": len(matrix),
            "n_skills": len(matrix.columns),
            "skills": list(matrix.columns),
        }

        return MatrixBuildResult(
            matrix=matrix, metadata=metadata, applied_transformers=applied_transformers
        )
