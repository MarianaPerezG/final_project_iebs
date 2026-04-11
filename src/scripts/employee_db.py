import sqlite3
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "config" / "database.db"


def init_database():
    """Ensure database directory exists."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def save_employee(
    employee_id: str,
    job_role: str,
    job_level: int,
    education: int,
    performance: int,
    current_skills: dict,
    target_skills: dict,
    gap_skills: dict,
    recommendations: list,
) -> bool:
    try:
        init_database()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO employees 
                (id, job_role, job_level, education, performance, current_skills, 
                 target_skills, gap_skills, recommendations, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    employee_id,
                    job_role,
                    job_level,
                    education,
                    performance,
                    json.dumps(current_skills),
                    json.dumps(target_skills),
                    json.dumps(gap_skills),
                    json.dumps(recommendations),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()

        logger.info(f"Saved employee: {employee_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving employee: {e}")
        return False


def get_employee(employee_id: str) -> dict:
    try:
        init_database()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, job_role, job_level, education, performance, current_skills,
                       target_skills, gap_skills, recommendations, created_at
                FROM employees
                WHERE id = ?
            """,
                (employee_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "job_role": row[1],
                "job_level": row[2],
                "education": row[3],
                "performance": row[4],
                "current_skills": json.loads(row[5]),
                "target_skills": json.loads(row[6]),
                "gap_skills": json.loads(row[7]),
                "recommendations": json.loads(row[8]),
                "created_at": row[9],
            }
    except Exception as e:
        logger.error(f"Error retrieving employee: {e}")
        return None


def save_gap_skills(
    employee_id: str, job_role: str, job_level: int, family: str, gap_skills: dict
) -> bool:
    try:
        init_database()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Build INSERT statement dynamically with gap_skills columns
            columns = ["EmployeeNumber", "JobRole", "JobLevel", "family"]
            values = [employee_id, job_role, job_level, family]
            placeholders = ["?"] * len(columns)

            # Add skill columns
            for skill, score in gap_skills.items():
                columns.append(skill)
                values.append(float(score))
                placeholders.append("?")

            insert_sql = f"""
                INSERT INTO gap_matrix ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """

            cursor.execute(insert_sql, values)
            conn.commit()

        logger.info(f"Saved gap_skills for employee: {employee_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving gap_skills: {e}")
        return False


def get_gap_skills_from_matrix(employee_id: str, global_skills: list = None) -> dict:
    try:
        init_database()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Get all columns from gap_matrix
            cursor.execute("PRAGMA table_info(gap_matrix)")
            all_columns = [row[1] for row in cursor.fetchall()]

            # Determine which columns are skills (exclude metadata)
            metadata_cols = {"EmployeeNumber", "JobRole", "JobLevel", "family"}
            skill_columns = [col for col in all_columns if col not in metadata_cols]

            if not skill_columns:
                logger.warning(f"No skill columns found in gap_matrix")
                return {}

            # Build SELECT with only skill columns
            select_cols = ", ".join([f'"{col}"' for col in skill_columns])
            query = f"""
                SELECT {select_cols}
                FROM gap_matrix
                WHERE EmployeeNumber = ?
            """

            cursor.execute(query, (employee_id,))
            row = cursor.fetchone()

            if not row:
                return {}

            # Convert to dict
            gap_dict = {}
            for col, value in zip(skill_columns, row):
                if value is not None:
                    gap_dict[col] = float(value)

            return gap_dict
    except Exception as e:
        logger.error(f"Error retrieving gap_skills from matrix: {e}")
        return {}
