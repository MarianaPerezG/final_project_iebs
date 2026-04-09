from pathlib import Path
from venv import logger

import pandas as pd

from config.global_skills import GLOBAL_SKILLS
from schemas import TargetMatrixConfig
from scripts.save_data import save_dataframe_to_csv
from target_matrix.builder import TargetMatrixBuilder


def create_target_matrix(config: TargetMatrixConfig) -> None:
    pass
