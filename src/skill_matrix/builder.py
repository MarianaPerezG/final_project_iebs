from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import pandas as pd

from .schemas import MatrixBuildResult
from .transformers import BaseMatrixTransformer


@dataclass
class SkillMatrixBuilder:
    global_skill_map: List[str] 
    transformers: List[BaseMatrixTransformer] = field(default_factory=list)

    def build(self, df: pd.DataFrame, global_skills: List[str] ) -> MatrixBuildResult:
   
        missing_columns = [skill for skill in self.global_skills if skill not in df.columns]

        if missing_columns:
            raise ValueError(
                f"Missing columns required for building the Skill Matrix: {missing_columns}"
            )


        matrix = df[self.global_skills].copy()

        applied_transformers = []
        for transformer in self.transformers:
            matrix = transformer.apply(matrix, df)
            applied_transformers.append(transformer.name)

        for global_skill, cols in self.global_skill_map.items():
            matrix[global_skill] = df[cols].mean(axis=1)


        metadata = {
            "n_rows": len(matrix),
            "n_skills": len(matrix.columns),
            "skills": list(matrix.columns),
        }

        return MatrixBuildResult(
            matrix=matrix,
            metadata=metadata,
            applied_transformers=applied_transformers
        )