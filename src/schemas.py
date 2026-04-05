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
class DownloadConfig:
    dataset_ref: str
    output_path: str = "src/data/raw"


@dataclass
class SkillMatrixConfig:
    dataset_path: str
    final_output_path: str


@dataclass
class TargetSkillMatrixConfig:
    dataset_path: str
    output_path: str


@dataclass
class TableConfig:
    name: str
    csv_path: str


@dataclass
class DatabaseConfig:
    tables: List[TableConfig]
    db_path: str = "src/config/database.db"


@dataclass
class JobPosting:
    title: str
    associated_skills: List[str]


@dataclass
class JobPostingsResponse:
    job_postings: List[JobPosting]
