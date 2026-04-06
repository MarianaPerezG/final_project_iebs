"""Add employee page."""

import streamlit as st
from pathlib import Path
import sys

st.set_page_config(
    page_title="Agregar Empleado", layout="wide", initial_sidebar_state="expanded"
)

# Setup path
src_path = Path(__file__).parent.parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def main():
    st.title("Agregar Empleado")
    st.markdown("---")
    st.markdown("Esta página está en construcción.")


if __name__ == "__main__":
    main()
