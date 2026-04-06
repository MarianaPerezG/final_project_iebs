import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import os

st.set_page_config(page_title="Skill Matrix Viewer", layout="wide")

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add src directory to path for imports to work regardless of where script is executed
src_path = Path(__file__).parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Try to import recommendation functions and configuration (optional, graceful fallback)
try:
    from recommender.recommend_courses import recommend_for_user
    from config.datasets import COURSE_RECOMMENDATIONS_CONFIGURATION

    RECOMMENDATIONS_AVAILABLE = True
    logging.info("Recommendation module imported successfully")
except ImportError as e:
    RECOMMENDATIONS_AVAILABLE = False
    COURSE_RECOMMENDATIONS_CONFIGURATION = {}
    logging.warning(f"Recommendation module not available: {e}")


@st.cache_data
def load_skill_matrix():
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


def detect_display_name(df: pd.DataFrame) -> str:
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


def display_course_recommendations(
    emp_id: int, skill_cols: list, course_df: pd.DataFrame
):
    """
    Display top-3 course recommendations for an employee.

    Parameters:
    -----------
    emp_id : int
        Employee ID
    skill_cols : list
        List of global skill column names
    course_df : pd.DataFrame
        Course skills matrix
    """
    if not RECOMMENDATIONS_AVAILABLE:
        st.error(
            "❌ Sistema de recomendaciones no disponible. "
            "No se pudo importar el módulo de recomendaciones. "
            "Verifica que el proyecto esté correctamente instalado."
        )
        return

    if not COURSE_RECOMMENDATIONS_CONFIGURATION:
        st.error("❌ Configuración de rutas de modelo no disponible")
        return

    # Get model path from config
    model_path_str = COURSE_RECOMMENDATIONS_CONFIGURATION.get(
        "MODEL_PATH", "models/trained/course_recommendations_model.pkl"
    )
    model_path = Path(model_path_str)
    csv_path = Path(
        COURSE_RECOMMENDATIONS_CONFIGURATION.get(
            "BATCH_RECOMMENDATIONS_PATH", "data/final/course_recommendations.csv"
        )
    )

    # Check if model exists
    if not model_path.exists():
        st.warning(
            f"⚠️ Modelo no encontrado en: `{model_path}`\n\n"
            f"Para generar el modelo, ejecuta en la terminal:\n\n"
            f"```bash\n"
            f"cd /Users/mariana/Documents/Master\\ Data\\ Science/Proyecto\\ final/project\n"
            f"conda run -n proyecto_final_iebs python src/main.py\n"
            f"```"
        )
        return

    try:
        # Get recommendations (hybrid: cached or on-demand)
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

        # Display each recommendation as a card-like structure
        for rank, rec in enumerate(recs, 1):
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{rank}. {rec['course_title']}**")
                    st.caption(
                        f"Level: {rec['course_level']} | Score: {rec['final_score']:.3f}"
                    )

                    # Find course in matrix to get improved skills
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
                            for skill in improved_skills[:5]:  # Show top 5 skills
                                score = float(course_matches.iloc[0].get(skill, 0.0))
                                st.write(f"- {skill} ({score:.2f})")

                with col2:
                    st.metric("Similitud", f"{rec['cosine_similarity']:.3f}")

                st.divider()

    except Exception as e:
        st.error(f"❌ Error al cargar recomendaciones: {str(e)}")
        logging.error(f"Recommendation error for emp {emp_id}: {e}", exc_info=True)


def main():
    st.title("Employees Data")

    try:
        df = load_skill_matrix()
    except Exception as e:
        st.error(str(e))
        return

    display_name_col = detect_display_name(df)
    id_col = detect_id_column(df)

    st.sidebar.markdown("### Filtros")
    # ensure session state key exists for selection so we can clear it with a back button
    if "selected_emp" not in st.session_state:
        st.session_state["selected_emp"] = ""
    if "clear_selected_emp" not in st.session_state:
        st.session_state["clear_selected_emp"] = False

    # If a previous action set the clear flag, reset the selected_emp before creating the widget
    if st.session_state.get("clear_selected_emp", False):
        st.session_state["selected_emp"] = ""
        st.session_state["clear_selected_emp"] = False
    # employee id selector (bound to session state)
    ids = df[id_col].astype(str).tolist()
    selected_id = st.sidebar.selectbox(
        "Seleccionar EmployeeId", options=["", *sorted(set(ids))], key="selected_emp"
    )

    gap_df = load_gap_matrix()
    course_df = load_course_matrix()

    # if an employee id selected, show its row and associated gap
    if selected_id:
        try:
            # find skill matrix row
            row_mask = df[id_col].astype(str) == str(selected_id)
            emp_row = df[row_mask]
            st.markdown(f"## Detalle empleado: {selected_id}")
            # back button to clear selection and return to main list
            if st.button("← Volver"):
                # set a separate flag so we can clear the selectbox value before the widget is recreated
                st.session_state["clear_selected_emp"] = True
            if not emp_row.empty:
                st.write(emp_row.T)
            else:
                st.info("EmployeeId no encontrado en la skill matrix")

            if gap_df is not None and id_col in gap_df.columns:
                gap_mask = gap_df[id_col].astype(str) == str(selected_id)
                gap_row = gap_df[gap_mask]
                if not gap_row.empty:
                    # prepare comparison table between skill matrix and gap matrix
                    st.markdown("### Gap asociado")

                    # detect skill columns: numeric columns in df excluding id and display name
                    skill_cols = [
                        c
                        for c in df.columns
                        if c not in [display_name_col, id_col, "JobLevel"]
                        and pd.api.types.is_numeric_dtype(df[c])
                    ]
                    # keep only those that also exist in gap_row
                    skill_cols = [c for c in skill_cols if c in gap_row.columns]

                    if not skill_cols:
                        st.info(
                            "No se encontraron columnas de skill compatibles entre matrices"
                        )
                    else:
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

                        # compute top-3 gaps
                        top3 = comp_df["gap"].sort_values(ascending=False).head(3)
                        comp_df["top_gap"] = comp_df.index.isin(top3.index)

                        st.markdown("### Comparativa Skill vs Gap")
                        # format numeric columns
                        st.dataframe(
                            comp_df.style.format(
                                {"skill_score": "{:.2f}", "gap": "{:.2f}"}
                            )
                        )

                        st.markdown("**Top 3 skills con mayor gap:**")
                        for s, v in top3.items():
                            st.write(f"- {s}: {v:.2f}")

                        # Show course recommendations
                        if course_df is not None:
                            display_course_recommendations(
                                int(selected_id), skill_cols, course_df
                            )
                else:
                    st.info("No se encontró fila de gap para este EmployeeId")
            else:
                st.info("Gap matrix no disponible")
        except Exception as e:
            st.error(f"Error al mostrar datos del empleado: {e}")

    st.markdown("## Vista previa")
    st.dataframe(df.head(10))


if __name__ == "__main__":
    main()
