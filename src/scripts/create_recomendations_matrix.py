import logging
from pathlib import Path
from venv import logger
import pandas as pd
import json

from config.global_skills import GLOBAL_SKILLS
from recommender.skill_mapper import SkillMapper
from recommender.skill_normalizer import SkillNormalizer
from schemas import CourseSkillsMatrixConfig
from scripts.save_data import save_dataframe_to_csv


def _save_unmapped_skills_report(skill_mapper: SkillMapper, report_path: str):
    report = skill_mapper.get_mapping_report()

    if not report["unmapped_skills"]:
        logger.info("No unmapped skills found")
        return

    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    unmapped_data = [
        {"skill": skill, "best_match": best_match, "confidence": float(confidence)}
        for skill, best_match, confidence in report["unmapped_skills"]
    ]

    with open(path, "w") as f:
        json.dump(
            {"total_unmapped": len(unmapped_data), "unmapped_skills": unmapped_data},
            f,
            indent=2,
        )

    logging.info(f"Unmapped skills report saved to: {path.absolute()}")


def create_recommendations_matrix(config: CourseSkillsMatrixConfig):

    courses_response = config.courses_response
    logging.info(
        f"✓ {len(courses_response.courses)} courses received from API response"
    )

    skill_mapper = SkillMapper(
        global_skills=list(GLOBAL_SKILLS), threshold=config.mapping_threshold
    )

    course_data = []
    for course in courses_response.courses:
        normalized_skills = [
            SkillNormalizer.normalize(s) for s in course.associated_skills
        ]
        mapped_skills = skill_mapper.map_skills(normalized_skills)

        course_data.append(
            {
                "course_title": course.title,
                "original_skills": ", ".join(course.associated_skills),
                "mapped_skills": mapped_skills,
            }
        )

    report = skill_mapper.get_mapping_report()
    logging.info(f"Total de skills processed: {report['total_mappings']}")
    logging.info(f"Total de skills unmapped: {len(report['unmapped_skills'])}")

    _save_unmapped_skills_report(skill_mapper, config.report_path)

    matrix_data = []
    for course in course_data:
        row = {
            "course_title": course["course_title"],
            **{
                skill: (1 if skill in course["mapped_skills"] else 0)
                for skill in GLOBAL_SKILLS
            },
        }
        matrix_data.append(row)

    course_skills_matrix = pd.DataFrame(matrix_data)

    skill_cols = [c for c in course_skills_matrix.columns if c in GLOBAL_SKILLS]
    if skill_cols:
        filtered_matrix = course_skills_matrix[
            course_skills_matrix[skill_cols].sum(axis=1) > 0
        ]
    else:
        filtered_matrix = course_skills_matrix

    if filtered_matrix.empty:
        logging.warning(
            "No courses with mapped skills found. Skipping saving course skills matrix."
        )
    else:
        save_dataframe_to_csv(filtered_matrix, config.output_path)
        logging.info(f"Final recommendation matrix saved to: {config.output_path}")
        logging.info(
            f"Saved {len(filtered_matrix)} courses out of {len(course_skills_matrix)}"
        )
