import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import random

from config.datasets import (
    RECOMMENDATION_MATRIX_CONFIGURATION,
    RECOMMENDATIONS_METRICS_CONFIGURATION,
)
from config.global_skills import GLOBAL_SKILLS
from recommender.create_recommendation_model import (
    CourseRecommendationModel,
    CourseRecommender,
)
from config.levels import get_course_level_number
from schemas import RecommendationConfig


class RecommendationEvaluator:
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.model = CourseRecommendationModel(
            gap_matrix_path=config.gap_matrix_path,
            course_matrix_path=config.course_matrix_path,
        )
        self.recommender = CourseRecommender(self.model)
        self.gap_matrix = self.model.gap_matrix
        self.course_matrix = self.model.course_matrix

        try:
            self.recommendations_df = pd.read_csv(config.recommendations_output_path)
            logging.info(
                f"Loaded recommendations from {config.recommendations_output_path}"
            )
        except FileNotFoundError:
            logging.warning(
                f"Recommendations CSV not found at {config.recommendations_output_path}"
            )
            self.recommendations_df = pd.DataFrame()

    def calculate_coverage(self) -> float:
        if self.recommendations_df.empty:
            return 0.0
        covered_employees = self.recommendations_df["employee_number"].nunique()
        total_employees = self.gap_matrix["EmployeeNumber"].nunique()
        return 100 * covered_employees / total_employees

    def calculate_skill_match_ratio(self, topk: int = 3) -> float:
        if self.recommendations_df.empty:
            return 0.0

        total_matches = 0
        total_gaps = 0

        for emp_num in self.recommendations_df["employee_number"].unique():
            try:
                user_row = self.gap_matrix[
                    self.gap_matrix["EmployeeNumber"] == emp_num
                ].iloc[0]
                gap_skills = [
                    skill
                    for skill in GLOBAL_SKILLS
                    if float(user_row.get(skill, 0.0)) > 0
                ]

                emp_recommendations = self.recommendations_df[
                    self.recommendations_df["employee_number"] == emp_num
                ]

                for _, reccomendation in emp_recommendations.iterrows():
                    course_title = reccomendation["course_title"]
                    course_row = self.course_matrix[
                        self.course_matrix["course_title"] == course_title
                    ]
                    if not course_row.empty:
                        course_row = course_row.iloc[0]
                        taught_skills = [
                            skill
                            for skill in GLOBAL_SKILLS
                            if float(course_row.get(skill, 0.0)) > 0.2
                        ]

                        matches = len(set(gap_skills) & set(taught_skills))
                        total_matches += matches
                        total_gaps += len(gap_skills) if gap_skills else 1

            except Exception as e:
                logging.warning(f"Could not evaluate employee {emp_num}: {e}")
                continue

        if total_gaps == 0:
            return 0.0
        return total_matches / total_gaps

    def calculate_semantic_stats(self) -> Dict[str, float]:
        if self.recommendations_df.empty:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}

        all_semantic_scores = self.recommendations_df["semantic_similarity"].tolist()

        if not all_semantic_scores:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}

        return {
            "mean": float(np.mean(all_semantic_scores)),
            "std": float(np.std(all_semantic_scores)),
            "min": float(np.min(all_semantic_scores)),
            "max": float(np.max(all_semantic_scores)),
        }

    def calculate_level_compatibility(self) -> Dict[str, float]:

        if self.recommendations_df.empty:
            return {"percentage": 0.0}

        within_level = 0
        total_recs = 0

        for emp_num in self.recommendations_df["employee_number"].unique():
            try:
                user_row = self.gap_matrix[
                    self.gap_matrix["EmployeeNumber"] == emp_num
                ].iloc[0]
                emp_level = int(user_row.get("JobLevel", 3))

                emp_recs = self.recommendations_df[
                    self.recommendations_df["employee_number"] == emp_num
                ]
                for _, rec in emp_recs.iterrows():
                    course_level_str = rec["course_level"]
                    course_level = get_course_level_number(course_level_str)
                    if abs(course_level - emp_level) <= 2:
                        within_level += 1
                    total_recs += 1

            except Exception as e:
                logging.warning(f"Could not evaluate employee {emp_num}: {e}")
                continue

        if total_recs == 0:
            return {"percentage": 0.0}
        return {"percentage": 100 * within_level / total_recs}

    def sample_employees_for_manual_validation(self, n_samples: int = 10) -> List[int]:
        all_employees = self.gap_matrix["EmployeeNumber"].unique().tolist()
        return random.sample(all_employees, min(n_samples, len(all_employees)))

    def generate_evaluation_report(self) -> Dict:
        logging.info("Generating evaluation report")

        report = {
            "coverage": self.calculate_coverage(),
            "skill_match_ratio": self.calculate_skill_match_ratio(),
            "semantic_stats": self.calculate_semantic_stats(),
            "level_compatibility": self.calculate_level_compatibility(),
        }

        return report

    def save_evaluation_report(self, report: Dict, output_path: str):
        path_obj = Path(output_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("RECOMMENDATION MODEL EVALUATION REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write("1. COVERAGE METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(
                f"Coverage (% employees with recommendations): {report['coverage']:.2f}%\n"
            )

            f.write("\n2. SKILL ALIGNMENT METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(
                f"Skill Match Ratio (gap vs taught): {report['skill_match_ratio']:.4f}\n"
            )
            f.write(
                f"Reading: For every gap skill, {report['skill_match_ratio']:.2%} is addressed\n"
            )

            f.write("\n3. DIVERSITY METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Reading: Higher is better (recommendations vary in quality)\n")

            f.write("\n4. SEMANTIC SIMILARITY METRICS\n")
            f.write("-" * 80 + "\n")
            semantic = report["semantic_stats"]
            f.write(f"Mean Semantic Score: {semantic['mean']:.4f}\n")
            f.write(f"Std Dev: {semantic['std']:.4f}\n")
            f.write(f"Range: [{semantic['min']:.4f}, {semantic['max']:.4f}]\n")
            f.write(
                f"Reading: Average coherence between employee gaps and courses (0-1)\n"
            )

            f.write("\n5. LEVEL COMPATIBILITY METRICS\n")
            f.write("-" * 80 + "\n")
            level = report["level_compatibility"]["percentage"]
            f.write(f"Within ±2 Level: {level:.2f}%\n")
            f.write(f"Reading: % of courses at appropriate difficulty level\n")

        logging.info(f"Evaluation report saved to: {output_path}")


def run_evaluation(config: RecommendationConfig):

    evaluator = RecommendationEvaluator(config)

    report = evaluator.generate_evaluation_report()
    evaluator.save_evaluation_report(
        report, RECOMMENDATIONS_METRICS_CONFIGURATION["EVALUATION_REPORT_OUTPUT_PATH"]
    )

    logging.info("Recommendation model evaluation complete.")
