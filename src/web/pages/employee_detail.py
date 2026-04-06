from json import load

import streamlit as st
import pandas as pd
from pathlib import Path
import logging
import sys

src_path = Path(__file__).parent.parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO)

from web.utils.loaders import load
from config.levels import get_job_level_name

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)


def display_course_recommendations(emp_id: int):
    """Muestra todos los cursos recomendados para un empleado desde el CSV."""

    csv_path = Path("data/final/course_recommendations.csv")

    if not csv_path.exists():
        st.warning(
            "⚠️ Archivo de recomendaciones no encontrado. Ejecuta `python src/main.py` primero."
        )
        return

    try:
        recs_df = pd.read_csv(csv_path)
        emp_recs = recs_df[recs_df["employee_number"] == int(emp_id)]

        if emp_recs.empty:
            st.info("ℹ️ No se encontraron recomendaciones para este empleado")
            return

        st.markdown("### Cursos Recomendados")

        # Ordenar por rank
        emp_recs = emp_recs.sort_values("rank")

        for _, rec in emp_recs.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1.5, 1.5])

                with col1:
                    st.markdown(f"**{int(rec['rank'])}. {rec['course_title']}**")
                    st.caption(
                        f"📊 Level: {rec['course_level']} | Subject: {rec['course_subject']}"
                    )

                with col2:
                    st.metric("Score Final", f"{rec['final_score']:.4f}")

                with col3:
                    st.metric("Similitud", f"{rec['cosine_similarity']:.4f}")

                st.divider()

    except Exception as e:
        st.error(f"❌ Error al cargar recomendaciones: {str(e)}")
        logging.error(f"Error loading recommendations: {e}", exc_info=True)


def main():
    st.set_page_config(page_title="Employee Detail", layout="wide")

    st.title("Detalle del Empleado")

    if "selected_emp" not in st.session_state:
        st.warning("Por favor, selecciona un empleado desde la página principal")
        return

    selected_id = st.session_state.get("selected_emp")
    if not selected_id:
        st.warning("Por favor, selecciona un empleado desde la página principal")
        return

    try:
        df = load("data/final/skill_matrix_result.csv")
        gap_df = load("data/final/gap_matrix_result.csv")
        course_df = load("data/final/course_skills_matrix.csv")
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return

    display_name_col = "JobRole"
    id_col = "EmployeeNumber"

    # Back button
    if st.button("← Volver a la lista"):
        st.session_state["selected_emp"] = ""
        st.rerun()

    # Display employee data
    row_mask = df[id_col].astype(str) == str(selected_id)
    emp_row = df[row_mask]

    if emp_row.empty:
        st.error("Empleado no encontrado")
        return

    # Employee information
    st.markdown(f"## {display_name_col}: {emp_row.iloc[0][display_name_col]}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Employee ID", int(selected_id))
    with col2:
        if "JobLevel" in emp_row.columns:
            job_level = int(emp_row.iloc[0]["JobLevel"])
            job_level_name = get_job_level_name(job_level)
            st.metric("Job Level", job_level_name)

    # Skills comparison
    if gap_df is not None and id_col in gap_df.columns:
        gap_mask = gap_df[id_col].astype(str) == str(selected_id)
        gap_row = gap_df[gap_mask]

        if not gap_row.empty:
            st.markdown("---")
            st.markdown("### Comparativa Skill vs Gap")

            skill_cols = [
                c
                for c in df.columns
                if c not in [display_name_col, id_col, "JobLevel", "JobRole"]
                and pd.api.types.is_numeric_dtype(df[c])
            ]
            skill_cols = [c for c in skill_cols if c in gap_row.columns]

            if skill_cols:
                emp_skills = emp_row.iloc[0][skill_cols].astype(float)
                gap_skills = gap_row.iloc[0][skill_cols].astype(float)

                comp_df = pd.DataFrame(
                    {
                        "skill": skill_cols,
                        "skill_score": emp_skills.values,
                        "gap": gap_skills.values,
                    }
                )
                comp_df = comp_df.set_index("skill")

                # Top-3 gaps
                top3 = comp_df["gap"].sort_values(ascending=False).head(3)
                comp_df["top_gap"] = comp_df.index.isin(top3.index)

                st.dataframe(
                    comp_df.style.format({"skill_score": "{:.2f}", "gap": "{:.2f}"}),
                    use_container_width=True,
                )

                st.markdown("**🎯 Top 3 skills con mayor gap:**")
                for s, v in top3.items():
                    st.write(f"- {s}: {v:.2f}")

                # Course recommendations
                if course_df is not None:
                    st.markdown("---")
                    display_course_recommendations(int(selected_id))


if __name__ == "__main__":
    main()
