import logging
from pathlib import Path
import sqlite3
import pandas as pd

from config.datasets import SKILL_MATRIX_CONFIGURATION


def create_database():
    DB_PATH = "src/config/database.db"

    csv_path = Path(SKILL_MATRIX_CONFIGURATION["FINAL_SKILL_MATRIX_OUTPUT_PATH"])

    skill_matrix = pd.read_csv(csv_path)

    conn = sqlite3.connect(DB_PATH)

    skill_matrix.to_sql("skills_matrix", conn, if_exists="replace", index=False)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table';
    """
    )

    tables = [row[0] for row in cursor.fetchall()]

    logging.info(f"Tables in database: {tables}")
    conn.close()

    print(f"Database created at: {DB_PATH}")
