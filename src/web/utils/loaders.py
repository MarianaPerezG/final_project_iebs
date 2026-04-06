"""Utility functions for loading data."""

from pathlib import Path
import pandas as pd
import streamlit as st


@st.cache_data
def load_skill_matrix():
    """Load skill matrix from CSV."""
    candidates = [
        "data/processed/skill_matrix_result.csv",
        "data/final/skill_matrix_result.csv",
        "data/processed/skill_matrix.csv",
        "data/final/skill_matrix.csv",
    ]
    for p in candidates:
        path = Path(p)
        if path.exists():
            try:
                df = pd.read_csv(path)
                return df
            except Exception:
                continue
    raise FileNotFoundError(f"No skill matrix CSV found. Looked at: {candidates}")


@st.cache_data
def load_gap_matrix():
    """Load gap matrix from CSV."""
    path = Path("data/final/gap_matrix_result.csv")
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return None
    return None


@st.cache_data
def load_course_matrix():
    """Load course skills matrix for showing which skills each course improves."""
    candidates = [
        "data/final/course_skills_matrix.csv",
        "data/final/course_recommendations_matrix.csv",
    ]
    for p in candidates:
        path = Path(p)
        if path.exists():
            try:
                df = pd.read_csv(path)
                return df
            except Exception:
                continue
    return None
