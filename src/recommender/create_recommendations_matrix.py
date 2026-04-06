import logging
from pathlib import Path
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
        logging.info("No unmapped skills found")
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

        skills_conf = skill_mapper.score_skills(normalized_skills)

        subjects = course.subject

        subject_conf: dict = {g: 0.0 for g in skill_mapper.global_skills}
        for item in subjects:
            item_norm = SkillNormalizer.normalize(item)
            sc = skill_mapper.score_text(item_norm)
            for g, v in sc.items():
                subject_conf[g] = max(subject_conf.get(g, 0.0), v)

        title_norm = SkillNormalizer.normalize(course.title or "")
        title_conf = (
            skill_mapper.score_text(title_norm)
            if title_norm
            else {g: 0.0 for g in skill_mapper.global_skills}
        )

        course_data.append(
            {
                "course_title": course.title,
                "original_skills": ", ".join(course.associated_skills),
                "mapped_skills": mapped_skills,
                "level": course.level,
                "subject": subjects,
                "skills_conf": skills_conf,
                "subject_conf": subject_conf,
                "title_conf": title_conf,
            }
        )

    report = skill_mapper.get_mapping_report()
    logging.info(f"Total de skills processed: {report['total_mappings']}")
    logging.info(f"Total de skills unmapped: {len(report['unmapped_skills'])}")

    _save_unmapped_skills_report(skill_mapper, config.report_path)

    matrix_data = []
    WEIGHT_SKILL = 0.7
    WEIGHT_SUBJ = 0.2
    WEIGHT_TITLE = 0.1

    for course in course_data:
        row = {
            "course_title": course["course_title"],
            "level": course.get("level", ""),
            "subject": course.get("subject", ""),
        }

        for skill in GLOBAL_SKILLS:
            skill_score = float(course.get("skills_conf", {}).get(skill, 0.0))
            subj_score = float(course.get("subject_conf", {}).get(skill, 0.0))
            title_score = float(course.get("title_conf", {}).get(skill, 0.0))

            combined = (
                WEIGHT_SKILL * skill_score
                + WEIGHT_SUBJ * subj_score
                + WEIGHT_TITLE * title_score
            )
            combined = max(0.0, min(1.0, combined))
            row[skill] = round(combined, 2)

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
