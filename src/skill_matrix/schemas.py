from dataclasses import dataclass, field
from typing import Dict, List, Any
import pandas as pd


@dataclass
class MatrixBuildResult:
    matrix: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)
    applied_transformers: List[str] = field(default_factory=list)