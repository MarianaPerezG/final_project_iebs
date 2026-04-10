from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


# General
@dataclass
class DownloadConfig:
    dataset_ref: str
    output_path: str = "src/data/raw"


# Database
@dataclass
class TableConfig:
    name: str
    csv_path: str


@dataclass
class DatabaseConfig:
    tables: List[TableConfig]
    db_path: str = "src/config/database.db"


# Skill Matrix
@dataclass
class MatrixBuildResult:
    matrix: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)
    applied_transformers: List[str] = field(default_factory=list)


@dataclass
class SkillMatrixConfig:
    dataset_path: str
    final_output_path: str


# Target Matrix
@dataclass
class SkillDemandVectorConfig:
    dataset_path: str
    mapped_output_path: str
    skill_demand_output_path: str


@dataclass
class TargetMatrixConfig:
    skill_matrix_path: str
    skill_demand_path: str
    final_output_path: str


# Course API
@dataclass
class Course:
    title: str
    subject: List[str]
    level: str
    associated_skills: List[str]


@dataclass
class CoursesResponse:
    courses: List[Course]


# Course Recommendation
@dataclass
class CourseSkillsMatrixConfig:
    courses_response: CoursesResponse
    output_path: str
    report_path: str
    mapping_threshold: float = 0.65


@dataclass
class RecommendationConfig:
    gap_matrix_path: str
    course_matrix_path: str
    model_output_path: str
    recommendations_output_path: str
    top_k: int
