import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title="Skill Matrix Viewer", layout="wide")


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
                        if c not in [display_name_col, id_col]
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
