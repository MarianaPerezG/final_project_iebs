"""Employee detail page."""

import streamlit as st
import pandas as pd
from pathlib import Path
import logging
import sys

# Setup path
src_path = Path(__file__).parent.parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Setup logging
logging.basicConfig(level=logging.INFO)

# Import from utils and recommender
from web.utils.loaders import load_skill_matrix, load_gap_matrix, load_course_matrix
from web.utils.helpers import detect_display_name, detect_id_column, get_course_skills
from config.levels import get_job_level_name

try:
    from recommender.get_recommendations import recommend_for_user
    from config.datasets import COURSE_RECOMMENDATIONS_CONFIGURATION

    RECOMMENDATIONS_AVAILABLE = True
except ImportError as e:
    RECOMMENDATIONS_AVAILABLE = False
    COURSE_RECOMMENDATIONS_CONFIGURATION = {}
    logging.warning(f"Recommendation module not available: {e}")


def display_course_recommendations(
    emp_id: int, skill_cols: list, course_df: pd.DataFrame
):
    """Display top-3 course recommendations for an employee."""
    if not RECOMMENDATIONS_AVAILABLE:
        st.error(
            "❌ Sistema de recomendaciones no disponible. "
            "No se pudo importar el módulo de recomendaciones."
        )
        return

    if not COURSE_RECOMMENDATIONS_CONFIGURATION:
        st.error("❌ Configuración de rutas de modelo no disponible")
        return

    model_path_str = COURSE_RECOMMENDATIONS_CONFIGURATION.get(
        "MODEL_PATH", "models/trained/course_recommendations_model.pkl"
    )
    model_path = Path(model_path_str)
    csv_path = Path(
        COURSE_RECOMMENDATIONS_CONFIGURATION.get(
            "BATCH_RECOMMENDATIONS_PATH", "data/final/course_recommendations.csv"
        )
    )

    if not model_path.exists():
        st.warning(
            f"⚠️ Modelo no encontrado en: `{model_path}`\n\n"
            f"Para generar el modelo, ejecuta: `python src/main.py`"
        )
        return

    try:
        recs = recommend_for_user(
            user_id=emp_id,
            model_path=str(model_path.absolute()),
            csv_path=str(csv_path.absolute()) if csv_path.exists() else None,
            topk=3,
        )

        if not recs:
            st.info("ℹ️ No se encontraron recomendaciones para este empleado")
            return

        st.markdown("### 📚 Cursos Recomendados")

        for rank, rec in enumerate(recs, 1):
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{rank}. {rec['course_title']}**")
                    st.caption(
                        f"Level: {rec['course_level']} | Score: {rec['final_score']:.3f}"
                    )

                    course_matches = course_df[
                        course_df["course_title"].str.lower()
                        == rec["course_title"].lower()
                    ]

                    if not course_matches.empty:
                        improved_skills = get_course_skills(
                            course_matches.iloc[0], skill_cols, threshold=0.05
                        )
                        if improved_skills:
                            st.markdown("**Skills que mejora:**")
                            for skill in improved_skills[:5]:
                                score = float(course_matches.iloc[0].get(skill, 0.0))
                                st.write(f"- {skill} ({score:.2f})")

                with col2:
                    st.metric("Similitud", f"{rec['cosine_similarity']:.3f}")

                st.divider()

    except Exception as e:
        st.error(f"❌ Error al cargar recomendaciones: {str(e)}")
        logging.error(f"Recommendation error: {e}", exc_info=True)


def main():
    st.set_page_config(page_title="Employee Detail", layout="wide")
    st.title("📊 Detalle del Empleado")

    # Get employee ID from URL or session
    if "selected_emp" not in st.session_state:
        st.warning("Por favor, selecciona un empleado desde la página principal")
        return

    selected_id = st.session_state.get("selected_emp")
    if not selected_id:
        st.warning("Por favor, selecciona un empleado desde la página principal")
        return

    try:
        df = load_skill_matrix()
        gap_df = load_gap_matrix()
        course_df = load_course_matrix()
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return

    display_name_col = detect_display_name(df)
    id_col = detect_id_column(df)

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
        if "JobRole" in emp_row.columns:
            st.metric("Job Role", emp_row.iloc[0]["JobRole"])
    with col3:
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
            st.markdown("### 📈 Comparativa Skill vs Gap")

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
                    display_course_recommendations(
                        int(selected_id), skill_cols, course_df
                    )


if __name__ == "__main__":
    main()
