import streamlit as st
import pandas as pd
from pathlib import Path
import logging
import sys

st.set_page_config(
    page_title="Employee Courses Recommendations",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)


logging.basicConfig(level=logging.INFO)


src_path = Path(__file__).parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from web.utils.loaders import load
from config.levels import get_job_level_name


def main():
    st.title("Empleados")

    try:
        df = load("data/final/skill_matrix_result.csv")
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return

    id_col = "EmployeeNumber"
    display_name_col = "JobRole"

    st.markdown("###  Filtros")
    search_id = st.text_input(
        "Buscar por Employee ID", placeholder="Ingresa el ID del empleado..."
    )

    if search_id:
        df_filtered = df[
            df[id_col].astype(str).str.lower().str.contains(search_id.lower(), na=False)
        ]
    else:
        df_filtered = df

    st.markdown("---")

    # Crear encabezado de la tabla
    col1, col2, col3, col4 = st.columns([1.5, 3, 1.5, 1.5])
    with col1:
        st.markdown("**ID**")
    with col2:
        st.markdown("**Título de Trabajo**")
    with col3:
        st.markdown("**Nivel**")
    with col4:
        st.markdown("**Acción**")

    st.markdown("---")

    # Crear filas de la tabla
    for idx, (_, row) in enumerate(df_filtered.iterrows()):
        employee_id = str(row[id_col])
        employee_name = str(row[display_name_col])

        col1, col2, col3, col4 = st.columns([1.5, 3, 1.5, 1.5])

        with col1:
            st.write(employee_id)

        with col2:
            st.write(employee_name)

        with col3:
            if "JobLevel" in df.columns:
                job_level = int(row.get("JobLevel", 0))
                job_level_name = get_job_level_name(job_level)
                st.write(job_level_name)
            else:
                st.write("-")

        with col4:
            btn = st.button(
                "Ver detalle",
                key=f"btn_{employee_id}",
                use_container_width=True,
            )
            if btn:
                st.session_state["selected_emp"] = employee_id
                st.switch_page("pages/employee_detail.py")


if __name__ == "__main__":
    main()
