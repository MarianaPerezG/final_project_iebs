import sqlite3
import json
import logging
import re
from schemas import Course, CoursesResponse


class MockCourseAPI:
    def __init__(self, db_path: str = "src/config/database.db"):
        self.db_path = db_path

    def get_courses(self) -> CoursesResponse:
        return self._get_data_from_database()

    def _get_data_from_database(self) -> CoursesResponse:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT title, subject, level, associatedskills FROM course_recommendation"
                )
                rows = cursor.fetchall()

                if not rows:
                    logging.warning("No data found in course_recommendation table")
                    return CoursesResponse(courses=[])

                courses = []
                for row in rows:
                    title = row["title"]
                    subject_raw = row["subject"] or ""
                    level = row["level"]
                    skills_raw = row["associatedskills"]

                    cleaned = re.sub(r"\s*&\s*", ",", str(subject_raw))
                    cleaned = re.sub(r"[|;/]", ",", cleaned)
                    subject_list = [s.strip() for s in cleaned.split(",") if s.strip()]

                    try:
                        associated_skills = json.loads(skills_raw)
                        if not isinstance(associated_skills, list):
                            associated_skills = [associated_skills]
                    except (json.JSONDecodeError, TypeError):
                        associated_skills = [
                            s.strip() for s in str(skills_raw).split(",")
                        ]

                    courses.append(
                        Course(
                            title=title,
                            subject=subject_list,
                            level=level,
                            associated_skills=associated_skills,
                        )
                    )

                logging.info(f"Loaded {len(courses)} courses from database")
                return CoursesResponse(courses=courses)

        except sqlite3.OperationalError as e:
            logging.error(f"Database error: {e}")
            raise
        except Exception as e:
            logging.error(f"Error reading from database: {e}")
            raise
