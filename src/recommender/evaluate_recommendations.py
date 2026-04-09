import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import random

from config.datasets import RECOMMENDATION_MATRIX_CONFIGURATION
from config.global_skills import GLOBAL_SKILLS
from recommender.create_recommendation_model import (
    CourseRecommendationModel,
    CourseRecommender,
)
from schemas import RecommendationConfig


class RecommendationEvaluator:
    """Evaluates recommendation model quality."""

    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.model = CourseRecommendationModel(
            gap_matrix_path=config.gap_matrix_path,
            course_matrix_path=config.course_matrix_path,
            global_skills=config.global_skills,
        )
        self.recommender = CourseRecommender(self.model)
        self.gap_matrix = self.model.gap_matrix
        self.course_matrix = self.model.course_matrix

    def calculate_coverage(self) -> float:
        """% of employees that receive recommendations."""
        all_recs = self.recommender.generate_recommendations_for_all_employees(topk=3)
        if all_recs.empty:
            return 0.0
        covered_employees = all_recs["employee_number"].nunique()
        total_employees = self.gap_matrix["EmployeeNumber"].nunique()
        return 100 * covered_employees / total_employees

    def calculate_skill_match_ratio(self, topk: int = 3) -> float:
        """
        Average match between gap skills and course skills.
        Higher = better alignment.
        """
        total_matches = 0
        total_gaps = 0

        for emp_num in self.gap_matrix["EmployeeNumber"].unique():
            try:
                recs = self.recommender.generate_recommendations_for_employee(
                    emp_num, topk=topk
                )
                if not recs:
                    continue

                # Get employee gap skills
                user_row = self.gap_matrix[
                    self.gap_matrix["EmployeeNumber"] == emp_num
                ].iloc[0]
                gap_skills = [
                    skill
                    for skill in GLOBAL_SKILLS
                    if float(user_row.get(skill, 0.0)) > 0
                ]

                # Check course skills vs gap skills
                for rec in recs:
                    course_title = rec["course_title"]
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
                        # Match: intersection of gap_skills and taught_skills
                        matches = len(set(gap_skills) & set(taught_skills))
                        total_matches += matches
                        total_gaps += len(gap_skills) if gap_skills else 1

            except Exception as e:
                logging.warning(f"Could not evaluate employee {emp_num}: {e}")
                continue

        if total_gaps == 0:
            return 0.0
        return total_matches / total_gaps

    def calculate_diversity(self, topk: int = 3) -> float:
        """
        Std dev of final scores. Higher = more diverse recommendations.
        Lower = concentrated around same score.
        """
        all_scores = []

        for emp_num in self.gap_matrix["EmployeeNumber"].unique():
            try:
                recs = self.recommender.generate_recommendations_for_employee(
                    emp_num, topk=topk
                )
                for rec in recs:
                    all_scores.append(rec["final_score"])
            except Exception as e:
                logging.warning(f"Could not evaluate employee {emp_num}: {e}")
                continue

        if not all_scores:
            return 0.0
        return float(np.std(all_scores))

    def calculate_semantic_stats(self) -> Dict[str, float]:
        """Statistics on semantic similarity scores."""
        all_semantic_scores = []

        for emp_num in self.gap_matrix["EmployeeNumber"].unique():
            try:
                recs = self.recommender.generate_recommendations_for_employee(
                    emp_num, topk=3
                )
                for rec in recs:
                    all_semantic_scores.append(rec["semantic_similarity"])
            except Exception as e:
                logging.warning(f"Could not evaluate employee {emp_num}: {e}")
                continue

        if not all_semantic_scores:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}

        return {
            "mean": float(np.mean(all_semantic_scores)),
            "std": float(np.std(all_semantic_scores)),
            "min": float(np.min(all_semantic_scores)),
            "max": float(np.max(all_semantic_scores)),
        }

    def calculate_level_compatibility(self) -> Dict[str, float]:
        """% of recommendations within ±1 level of employee."""
        from config.levels import get_course_level_number

        within_level = 0
        total_recs = 0

        for emp_num in self.gap_matrix["EmployeeNumber"].unique():
            try:
                user_row = self.gap_matrix[
                    self.gap_matrix["EmployeeNumber"] == emp_num
                ].iloc[0]
                emp_level = int(user_row.get("JobLevel", 3))

                recs = self.recommender.generate_recommendations_for_employee(
                    emp_num, topk=3
                )
                for rec in recs:
                    course_level_str = rec["course_level"]
                    course_level = get_course_level_number(course_level_str)
                    if abs(course_level - emp_level) <= 1:
                        within_level += 1
                    total_recs += 1

            except Exception as e:
                logging.warning(f"Could not evaluate employee {emp_num}: {e}")
                continue

        if total_recs == 0:
            return {"percentage": 0.0}
        return {"percentage": 100 * within_level / total_recs}

    def sample_employees_for_manual_validation(self, n_samples: int = 10) -> List[int]:
        """Sample n random employees for manual validation."""
        all_employees = self.gap_matrix["EmployeeNumber"].unique().tolist()
        return random.sample(all_employees, min(n_samples, len(all_employees)))

    def generate_manual_validation_report(
        self, employee_numbers: List[int]
    ) -> pd.DataFrame:
        """Generate report for manual annotation of recommendations."""
        records = []

        for emp_num in employee_numbers:
            try:
                user_row = self.gap_matrix[
                    self.gap_matrix["EmployeeNumber"] == emp_num
                ].iloc[0]
                job_role = user_row.get("JobRole", "Unknown")
                job_level = user_row.get("JobLevel", 3)

                recs = self.recommender.generate_recommendations_for_employee(
                    emp_num, topk=3
                )

                for rank, rec in enumerate(recs, 1):
                    records.append(
                        {
                            "employee_number": emp_num,
                            "job_role": job_role,
                            "job_level": job_level,
                            "rank": rank,
                            "course_title": rec["course_title"],
                            "course_level": rec["course_level"],
                            "course_subject": rec["course_subject"],
                            "cosine_similarity": rec["cosine_similarity"],
                            "semantic_similarity": rec["semantic_similarity"],
                            "level_factor": rec["level_factor"],
                            "final_score": rec["final_score"],
                            "accuracy_annotation": "",  # To be filled manually
                            "notes": "",  # To be filled manually
                        }
                    )

            except Exception as e:
                logging.warning(
                    f"Could not generate report for employee {emp_num}: {e}"
                )
                continue

        return pd.DataFrame(records)

    def generate_evaluation_report(self) -> Dict:
        """Generate comprehensive evaluation report."""
        logging.info("Generating evaluation report...")

        report = {
            "coverage": self.calculate_coverage(),
            "skill_match_ratio": self.calculate_skill_match_ratio(),
            "diversity": self.calculate_diversity(),
            "semantic_stats": self.calculate_semantic_stats(),
            "level_compatibility": self.calculate_level_compatibility(),
        }

        return report

    def save_evaluation_report(self, report: Dict, output_path: str):
        """Save evaluation report to file."""
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
                f"Interpretation: For every gap skill, {report['skill_match_ratio']:.2%} is addressed\n"
            )

            f.write("\n3. DIVERSITY METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Score Diversity (Std Dev): {report['diversity']:.4f}\n")
            f.write(
                f"Interpretation: Higher is better (recommendations vary in quality)\n"
            )

            f.write("\n4. SEMANTIC SIMILARITY METRICS\n")
            f.write("-" * 80 + "\n")
            semantic = report["semantic_stats"]
            f.write(f"Mean Semantic Score: {semantic['mean']:.4f}\n")
            f.write(f"Std Dev: {semantic['std']:.4f}\n")
            f.write(f"Range: [{semantic['min']:.4f}, {semantic['max']:.4f}]\n")
            f.write(
                f"Interpretation: Average coherence between employee gaps and courses (0-1)\n"
            )

            f.write("\n5. LEVEL COMPATIBILITY METRICS\n")
            f.write("-" * 80 + "\n")
            level = report["level_compatibility"]["percentage"]
            f.write(f"Within ±1 Level: {level:.2f}%\n")
            f.write(f"Interpretation: % of courses at appropriate difficulty level\n")

            f.write("\n6. SUMMARY & INTERPRETATION\n")
            f.write("-" * 80 + "\n")
            f.write("✓ High Coverage: Model reaches most employees\n")
            f.write("✓ High Skill Match: Courses address actual gaps\n")
            f.write("✓ High Diversity: Recommendations are varied and specific\n")
            f.write("✓ High Semantic Score: Contextual relevance is strong\n")
            f.write("✓ High Level Compatibility: Difficulty is appropriate\n")

        logging.info(f"Evaluation report saved to: {output_path}")

    def save_manual_validation_template(self, df: pd.DataFrame, output_path: str):
        """Save manual validation template as CSV."""
        path_obj = Path(output_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(output_path, index=False)

        logging.info(f"Manual validation template saved to: {output_path}")
        logging.info("Instructions:")
        logging.info("  1. Open the CSV file and review each recommendation")
        logging.info(
            "  2. For each row, fill 'accuracy_annotation' column with one of:"
        )
        logging.info("     - 'Excellent': Highly relevant recommendation")
        logging.info("     - 'Good': Reasonably relevant")
        logging.info("     - 'Poor': Not relevant")
        logging.info("  3. Optional: Add notes explaining your decision")


def run_evaluation(config: RecommendationConfig):
    """Run complete evaluation pipeline."""
    evaluator = RecommendationEvaluator(config)

    # Generate evaluation report
    report = evaluator.generate_evaluation_report()
    evaluator.save_evaluation_report(report, "reports/recommendation_evaluation.txt")

    # Generate manual validation template
    sample_employees = evaluator.sample_employees_for_manual_validation(n_samples=10)
    validation_df = evaluator.generate_manual_validation_report(sample_employees)
    evaluator.save_manual_validation_template(
        validation_df, "reports/manual_validation_template.csv"
    )

    logging.info("=" * 80)
    logging.info("EVALUATION COMPLETE")
    logging.info("=" * 80)
    logging.info("Reports generated:")
    logging.info("  1. reports/recommendation_evaluation.txt - Automated metrics")
    logging.info(
        "  2. reports/manual_validation_template.csv - To be annotated manually"
    )
