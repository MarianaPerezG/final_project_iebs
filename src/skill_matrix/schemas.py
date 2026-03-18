from dataclasses import dataclass, field
from typing import Dict, List, Any
import pandas as pd
from pathlib import Path


@dataclass
class MatrixBuildResult:
    matrix: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)
    applied_transformers: List[str] = field(default_factory=list)


@dataclass
class SkillMatrixConfig:
    dataset_path: str
    output_path: str
    transformers: list[Any] = field(default_factory=list)
