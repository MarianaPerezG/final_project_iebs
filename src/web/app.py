from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import logging
import sys
import ast
from pathlib import Path


src_path = Path(__file__).parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
    print(f"Added to sys.path: {src_path}")

from config.datasets import (
    COMPANY_GOALS_CONFIGURATION,
    SKILL_MATRIX_CONFIGURATION,
    COURSE_RECOMMENDATIONS_CONFIGURATION,
    RECOMMENDATION_MATRIX_CONFIGURATION,
)
from config.global_skills import GLOBAL_SKILLS
from config.levels import get_job_level_name
from scripts.create_company_goals import create_company_goals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")


SKILL_COLUMNS = GLOBAL_SKILLS


def format_skill_name(skill_name):
    return skill_name.replace("_", " ").title()


@app.route("/")
def home():
    goals_df = pd.read_csv(COMPANY_GOALS_CONFIGURATION["COMPANY_GOALS_RAW_DATASET_REF"])
    company_goals = []

    if goals_df is not None:
        company_goals = [
            {
                "id": int(row["goal_id"]) if "goal_id" in row.index else index + 1,
                "goal": row["goal"],
            }
            for index, (_, row) in enumerate(goals_df.iterrows())
            if "goal" in row.index and str(row["goal"]).strip()
        ]

    saved = request.args.get("saved") == "1"

    return render_template(
        "company_home.html",
        company_goals=company_goals,
        saved=saved,
    )


@app.route("/employees")
def employee_directory():
    """Employee directory page."""
    search = request.args.get("search", "").lower()

    try:
        df = pd.read_csv(SKILL_MATRIX_CONFIGURATION["FINAL_SKILL_MATRIX_OUTPUT_PATH"])
    except Exception as e:
        logger.error(f"Error loading skill matrix: {e}")
        return "Error loading data", 500

    # Filter by search
    if search:
        df = df[
            df["EmployeeNumber"].astype(str).str.lower().str.contains(search, na=False)
            | df["JobRole"].str.lower().str.contains(search, na=False)
        ]

    # Prepare employee data
    employees = []
    for _, row in df.iterrows():
        emp_id = str(int(row["EmployeeNumber"]))
        emp_role = row["JobRole"] if "JobRole" in row.index else "-"
        emp_level = int(row["JobLevel"]) if "JobLevel" in row.index else 3
        emp_level_name = get_job_level_name(emp_level)

        employees.append(
            {
                "id": emp_id,
                "role": emp_role,
                "level": emp_level_name,
            }
        )

    return render_template("employees.html", employees=employees, search=search)


@app.route("/company-goals/new")
def new_company_goals():
    """Form to create or replace company goals."""
    goal_lines = ""
    try:
        existing_goals = pd.read_csv(
            COMPANY_GOALS_CONFIGURATION["COMPANY_GOALS_RAW_DATASET_REF"]
        )
    except FileNotFoundError:
        existing_goals = None

    if existing_goals is not None and "goal" in existing_goals.columns:
        goal_lines = "\n".join(
            str(goal).strip()
            for goal in existing_goals["goal"].tolist()
            if str(goal).strip()
        )

    return render_template("company_goals_form.html", goal_lines=goal_lines)


@app.route("/company-goals", methods=["POST"])
def save_company_goals():
    """Persist company goals into data/raw/company_goals.csv."""
    raw_goals = request.form.get("goals", "")
    goals = [line.strip() for line in raw_goals.splitlines() if line.strip()]

    if not goals:
        return render_template(
            "company_goals_form.html",
            goal_lines=raw_goals,
            error_message="Add at least one company goal before saving.",
        )

    create_company_goals(goals)
    return redirect(url_for("home", saved=1))


@app.route("/employee/<emp_id>")
def employee_detail(emp_id):
    """Employee detail page with recommendations."""
    try:
        df = pd.read_csv(SKILL_MATRIX_CONFIGURATION["FINAL_SKILL_MATRIX_OUTPUT_PATH"])
        gap_df = pd.read_csv(COURSE_RECOMMENDATIONS_CONFIGURATION["GAP_MATRIX_PATH"])
        course_df = pd.read_csv(
            RECOMMENDATION_MATRIX_CONFIGURATION[
                "FINAL_RECOMMENDATION_MATRIX_OUTPUT_PATH"
            ]
        )
        recommendations_df = pd.read_csv(
            COURSE_RECOMMENDATIONS_CONFIGURATION[
                "CURRENT_EMPLOYEES_RECOMMENDATIONS_PATH"
            ]
        )

        if df is None:
            return "Error loading data", 500

        # Get employee row
        emp_row = df[df["EmployeeNumber"].astype(str) == str(emp_id)]
        if emp_row.empty:
            return "Employee not found", 404

        emp_row = emp_row.iloc[0]
        emp_id_int = int(emp_id)
        emp_role = emp_row["JobRole"] if "JobRole" in emp_row.index else "-"
        emp_level = int(emp_row["JobLevel"]) if "JobLevel" in emp_row.index else 3
        emp_level_name = get_job_level_name(emp_level)

        # Get employee metrics
        gap_skills = []
        top_gap_skills = []

        if gap_df is not None:
            gap_row = gap_df[gap_df["EmployeeNumber"].astype(str) == str(emp_id)]
            if not gap_row.empty:
                gap_row = gap_row.iloc[0]
                gap_skills = [
                    {"skill": format_skill_name(col), "gap": float(gap_row[col])}
                    for col in SKILL_COLUMNS
                    if col in gap_row.index and float(gap_row[col]) > 0
                ]
                gap_skills = sorted(gap_skills, key=lambda x: x["gap"], reverse=True)
                top_gap_skills = gap_skills[:3]
                gap_skills = gap_skills[:10]

        # Get recommendations
        recommendations = []
        if (
            recommendations_df is not None
            and "employee_number" in recommendations_df.columns
        ):
            emp_recs = recommendations_df[
                recommendations_df["employee_number"].astype(str) == str(emp_id)
            ]
            if not emp_recs.empty:
                for _, rec in emp_recs.iterrows():
                    course_name = rec.get("course_title", "-")

                    # Get skills for this course
                    skills = []
                    if course_df is not None:
                        course_row = course_df[course_df["course_title"] == course_name]
                        if not course_row.empty:
                            course_row = course_row.iloc[0]
                            skills_scores = []
                            for skill in SKILL_COLUMNS:
                                if skill in course_row.index:
                                    score = course_row[skill]
                                    if score > 0:
                                        skills_scores.append((skill, score))
                            # Sort by score and get top 3
                            skills_scores.sort(key=lambda x: x[1], reverse=True)
                            skills = [
                                format_skill_name(s[0]) for s in skills_scores[:3]
                            ]

                    # Parse course subject
                    subjects = []
                    try:
                        subject_raw = rec.get("course_subject", "Recommended")
                        if isinstance(subject_raw, str):
                            # Try to parse as array
                            try:
                                subject_list = ast.literal_eval(subject_raw)
                                if isinstance(subject_list, list):
                                    subjects = subject_list
                            except (ValueError, SyntaxError):
                                # If it's not an array, just use as is
                                subjects = [subject_raw]
                        else:
                            subjects = [str(subject_raw)]
                    except Exception as e:
                        logger.warning(f"Error parsing subject: {e}")
                        subjects = ["Recommended"]

                    recommendations.append(
                        {
                            "course_id": rec.get("rank", "-"),
                            "course_name": course_name,
                            "subjects": subjects,
                            "skills": skills,
                        }
                    )

        return render_template(
            "detail.html",
            emp_id=emp_id,
            emp_role=emp_role,
            emp_level=emp_level_name,
            gap_skills=gap_skills,
            top_gap_skills=top_gap_skills,
            recommendations=recommendations,
        )

    except Exception as e:
        logger.error(f"Error in employee detail: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return f"Error: {str(e)}", 500


@app.route("/api/employees")
def api_employees():
    """API endpoint for employee search (for AJAX)."""
    search = request.args.get("q", "").lower()

    try:
        df = pd.read_csv(SKILL_MATRIX_CONFIGURATION["FINAL_SKILL_MATRIX_OUTPUT_PATH"])
    except Exception as e:
        logger.error(f"Error loading skill matrix: {e}")
        return jsonify([])

    if search:
        df = df[
            df["EmployeeNumber"].astype(str).str.lower().str.contains(search, na=False)
            | df["JobRole"].str.lower().str.contains(search, na=False)
        ]

    results = []
    for _, row in df.iterrows():
        emp_id = str(int(row["EmployeeNumber"]))
        emp_role = row["JobRole"] if "JobRole" in row.index else "-"
        results.append(
            {
                "id": emp_id,
                "role": emp_role,
            }
        )

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
