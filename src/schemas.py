from dataclasses import dataclass, field
from typing import Dict, List, Any
import pandas as pd
from pathlib import Path


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


# Target Skill Matrix
@dataclass
class TargetSkillMatrixConfig:
    dataset_path: str
    output_path: str


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
    output_path: str
    global_skills: List[str]
