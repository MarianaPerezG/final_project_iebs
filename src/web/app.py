"""Main home page - Employee list."""

import streamlit as st
import pandas as pd
from pathlib import Path
import logging
import sys

# Setup page config
st.set_page_config(
    page_title="Employee Skill Matrix", layout="wide", initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add src directory to path for imports to work regardless of where script is executed
src_path = Path(__file__).parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import utilities
from web.utils.loaders import load_skill_matrix
from web.utils.helpers import detect_display_name, detect_id_column
from config.levels import get_job_level_name


def main():
    st.title("👥 Empleados")
    st.markdown("Explora la matriz de habilidades de todos los empleados")

    try:
        df = load_skill_matrix()
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return

    display_name_col = detect_display_name(df)
    id_col = detect_id_column(df)

    # Filters
    st.sidebar.markdown("### 🔍 Filtros")

    # Search by name
    search_name = st.sidebar.text_input(
        "Buscar por nombre", placeholder="Ingresa parte del nombre..."
    )

    # Filter dataframe by search
    if search_name:
        df_filtered = df[
            df[display_name_col]
            .astype(str)
            .str.lower()
            .str.contains(search_name.lower(), na=False)
        ]
    else:
        df_filtered = df

    st.markdown(f"### Mostrando {len(df_filtered)} de {len(df)} empleados")

    # Display employees as selectable items
    st.markdown("---")

    # Create columns for better layout
    cols_per_row = 2
    cols = st.columns(cols_per_row)

    for idx, (_, row) in enumerate(df_filtered.iterrows()):
        employee_id = str(row[id_col])
        employee_name = str(row[display_name_col])

        col = cols[idx % cols_per_row]

        with col:
            # Create a card-like container
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{employee_name}**")
                    st.caption(f"ID: {employee_id}")

                    # Show JobLevel if available
                    if "JobLevel" in df.columns:
                        job_level = int(row.get("JobLevel", 0))
                        job_level_name = get_job_level_name(job_level)
                        st.caption(f"📊 Level: {job_level_name}")

                    # Show key metrics if available
                    skill_metrics = []
                    for c in df.columns:
                        if c not in [
                            display_name_col,
                            id_col,
                            "JobLevel",
                            "JobRole",
                        ] and pd.api.types.is_numeric_dtype(df[c]):
                            skill_metrics.append((c, float(row.get(c, 0))))

                    if skill_metrics:
                        top_skill = max(skill_metrics, key=lambda x: x[1])
                        st.markdown(f"Top skill: {top_skill[0]}")

                with col2:
                    btn = st.button(
                        "Ver detalle",
                        key=f"btn_{employee_id}",
                        use_container_width=True,
                    )
                    if btn:
                        st.session_state["selected_emp"] = employee_id
                        st.switch_page("pages/employee_detail.py")

    # Summary section
    st.markdown("---")
    st.markdown("### 📊 Resumen General")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Empleados", len(df))
    with col2:
        st.metric("Empleados Mostrados", len(df_filtered))
    with col3:
        st.metric("Columnas de Datos", len(df.columns))

    # Show data table option
    st.markdown("---")
    if st.checkbox("Mostrar tabla de datos", value=False):
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
