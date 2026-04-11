import logging
import sqlite3
from pathlib import Path

import pandas as pd

from schemas import DatabaseConfig


def create_database(config: DatabaseConfig):
    db_path = config.db_path

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for table_config in config.tables:
            table_name = table_config.name

            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table' AND name=?;
            """,
                (table_name,),
            )
            table_exists = cursor.fetchone() is not None

            if table_config.sql_schema:
                if table_exists:
                    logging.info(
                        "Table '%s' already exists. Skipping creation.",
                        table_name,
                    )
                else:
                    logging.info(
                        "Table '%s' does not exist. Creating from schema.", table_name
                    )
                    cursor.execute(table_config.sql_schema)
                    conn.commit()
            else:
                csv_path = Path(table_config.csv_path)

                if not csv_path.exists():
                    raise FileNotFoundError(
                        f"CSV not found for table '{table_name}': {csv_path}"
                    )

                if csv_path.suffix.lower() != ".csv":
                    raise ValueError(
                        f"File must be CSV for table '{table_name}': {csv_path}"
                    )

                df = pd.read_csv(csv_path)

                if table_exists:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    row_count = cursor.fetchone()[0]

                    if row_count > 0:
                        logging.info(
                            "Table '%s' already exists with %d rows. Skipping load.",
                            table_name,
                            row_count,
                        )
                    else:
                        logging.info(
                            "Table '%s' exists but is empty. Loading data.", table_name
                        )
                        df.to_sql(table_name, conn, if_exists="append", index=False)
                else:
                    logging.info(
                        "Table '%s' does not exist. Creating and loading data.",
                        table_name,
                    )
                    df.to_sql(table_name, conn, if_exists="fail", index=False)

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table';
        """
        )
        tables = [row[0] for row in cursor.fetchall()]
        logging.info("Tables in database: %s", tables)

        for table in tables:
            if not table.isidentifier():
                continue
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            logging.info("Table '%s' has %d records", table, count)

    logging.info("Database ready at: %s", db_path)
