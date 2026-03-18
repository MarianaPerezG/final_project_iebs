from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd


class BaseMatrixTransformer(ABC):
    name: str = "base_transformer"

    @abstractmethod
    def apply(self, matrix: pd.DataFrame, source_df: pd.DataFrame) -> pd.DataFrame:
        pass