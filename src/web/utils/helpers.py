"""Helper functions for the web app."""

import pandas as pd


def detect_display_name(df: pd.DataFrame) -> str:
    """Detect the display name column in the dataframe."""
    possible = ["full_name", "fullname", "name", "employee_name", "display_name"]
    for c in df.columns:
        if c.lower() in possible:
            return c
    # fallback to first non-numeric column if exists
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            return c
    return df.columns[0]


def detect_id_column(df: pd.DataFrame) -> str:
    """Detect the ID column in the dataframe."""
    candidates = [
        "EmployeeNumber",
        "employee_number",
        "employeeid",
        "employee_id",
        "id",
    ]
    for c in df.columns:
        if c in candidates or c.lower() in [x.lower() for x in candidates]:
            return c
    # fallback to first numeric column
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            return c
    return df.columns[0]


def get_course_skills(
    course_row: pd.Series, skill_cols: list, threshold: float = 0.1
) -> list:
    """
    Extract skills that are improved by a course (skills with score > threshold).

    Parameters:
    -----------
    course_row : pd.Series
        Row from course_skills_matrix
    skill_cols : list
        List of skill column names
    threshold : float
        Minimum score to consider a skill as improved (default 0.1)

    Returns:
    --------
    list
        List of skill names with non-zero scores, sorted by score descending
    """
    skills_with_scores = []
    for skill in skill_cols:
        if skill in course_row.index:
            score = float(course_row.get(skill, 0.0))
            if score > threshold:
                skills_with_scores.append((skill, score))

    # Sort by score descending
    skills_with_scores.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in skills_with_scores]
