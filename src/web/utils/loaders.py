"""Utility functions for loading data."""

from pathlib import Path
import pandas as pd
import streamlit as st


@st.cache_data
def load(path: str):

    csv_path = Path(path)
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            st.error(f"Error loading CSV at {csv_path}: {e}")
            return None
    else:
        st.warning(f"CSV file not found at: {csv_path}")
        return None
