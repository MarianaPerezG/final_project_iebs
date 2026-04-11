from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import logging
import sys
import ast
from pathlib import Path
import threading

# Add src directory to path BEFORE importing local modules
src_path = Path(__file__).parent.parent.absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from scripts.employee_calculator import (
    calculate_employee_skills,
    calculate_target_skills,
    calculate_gap_skills,
    get_course_recommendations,
)
from scripts.employee_db import save_employee, save_gap_skills
from config.scoring_rules import ROLE_TO_FAMILY

from config.datasets import (
    COMPANY_GOAL_SKILLS_CONFIGURATION,
    SKILL_MATRIX_CONFIGURATION,
    COURSE_RECOMMENDATIONS_CONFIGURATION,
    RECOMMENDATION_MATRIX_CONFIGURATION,
)
from config.global_skills import GLOBAL_SKILLS
from config.levels import get_job_level_name
from target_matrix.create_company_goals import create_company_goals
from scripts.pipelines import recalculate_pipeline_from_new_company_goal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Global state for pipeline processing
pipeline_state = {"processing": False, "status": "idle", "progress": 0, "message": ""}


def _run_pipeline_thread():
    """Wrapper to run pipeline in background thread."""
    global pipeline_state

    try:
        pipeline_state["processing"] = True
        pipeline_state["status"] = "process"

        # Run the actual pipeline recalculation
        recalculate_pipeline_from_new_company_goal()

        pipeline_state["status"] = "complete"
        pipeline_state["progress"] = 100
        pipeline_state["message"] = "Pipeline completed!"
        logger.info("Pipeline recalculation thread finished successfully")

    except Exception as e:
        pipeline_state["status"] = "error"
        pipeline_state["message"] = f"Error: {str(e)}"
        logger.error(f"Pipeline thread failed: {e}", exc_info=True)

    finally:
        pipeline_state["processing"] = False


SKILL_COLUMNS = GLOBAL_SKILLS


def format_skill_name(skill_name):
    return skill_name.replace("_", " ").title()


@app.route("/")
def home():
    company_goals = []
    saved = request.args.get("saved") == "1"

    try:
        goals_df = pd.read_csv(COMPANY_GOAL_SKILLS_CONFIGURATION["COMPANY_GOALS_PATH"])

        if goals_df is not None and not goals_df.empty:
            company_goals = [
                {
                    "id": int(row["goal_id"]) if "goal_id" in row.index else index + 1,
                    "goal": row["goal"],
                }
                for index, (_, row) in enumerate(goals_df.iterrows())
                if "goal" in row.index and str(row["goal"]).strip()
            ]
    except pd.errors.EmptyDataError:
        logger.info("Company goals file is empty")
        company_goals = []
    except FileNotFoundError:
        logger.warning(
            f"Company goals file not found at {COMPANY_GOAL_SKILLS_CONFIGURATION['COMPANY_GOALS_PATH']}"
        )
        company_goals = []

    return render_template(
        "company_home.html",
        company_goals=company_goals,
        saved=saved,
    )


@app.route("/employees")
def employee_directory():
    """Employee directory page."""
    from scripts.employee_db import init_database
    import sqlite3

    search = request.args.get("search", "").lower()

    try:
        df = pd.read_csv(SKILL_MATRIX_CONFIGURATION["FINAL_SKILL_MATRIX_OUTPUT_PATH"])
    except Exception as e:
        logger.error(f"Error loading skill matrix: {e}")
        return "Error loading data", 500

    # Prepare employee data from CSV
    employees = []
    for _, row in df.iterrows():
        emp_id = str(int(row["EmployeeNumber"]))
        emp_role = row["JobRole"] if "JobRole" in row.index else "-"
        emp_level = int(row["JobLevel"]) if "JobLevel" in row.index else 3
        emp_level_name = get_job_level_name(emp_level)

        employees.append({"id": emp_id, "role": emp_role, "level": emp_level_name})

    # Add employees from database
    try:
        init_database()
        from pathlib import Path as PathlibPath

        db_path = PathlibPath(__file__).parent.parent / "config" / "database.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, job_role, job_level FROM employees ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()

            for row in rows:
                emp_id = row[0]
                emp_role = row[1]
                emp_level_name = get_job_level_name(row[2])

                employees.append(
                    {"id": emp_id, "role": emp_role, "level": emp_level_name}
                )
    except Exception as e:
        logger.warning(f"Could not load employees: {e}")

    # Filter by search
    if search:
        employees = [
            emp
            for emp in employees
            if search in emp["id"].lower() or search in emp["role"].lower()
        ]

    return render_template("employees.html", employees=employees, search=search)


@app.route("/company-goals/new")
def new_company_goals():
    """Form to create or replace company goals."""
    goal_lines = ""
    try:
        existing_goals = pd.read_csv(
            COMPANY_GOAL_SKILLS_CONFIGURATION["COMPANY_GOALS_PATH"]
        )
    except (FileNotFoundError, pd.errors.EmptyDataError):
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
    raw_goals = request.form.get("goals", "")
    goals = [line.strip() for line in raw_goals.splitlines() if line.strip()]

    if not goals:
        return render_template(
            "company_goals_form.html",
            goal_lines=raw_goals,
            error_message="Add at least one company goal before saving.",
        )

    # Save company goals
    create_company_goals(goals)

    # Start pipeline recalculation in background thread
    pipeline_thread = threading.Thread(target=_run_pipeline_thread, daemon=True)
    pipeline_thread.start()

    return redirect(url_for("home", saved=1))


@app.route("/api/company-goals", methods=["POST"])
def api_save_company_goals():
    """API endpoint to save goals and trigger pipeline recalculation."""
    data = request.get_json()
    goals = data.get("goals", [])

    if not goals or not isinstance(goals, list):
        return jsonify({"error": "Invalid goals format"}), 400

    goals = [g.strip() for g in goals if isinstance(g, str) and g.strip()]

    if not goals:
        return jsonify({"error": "At least one goal is required"}), 400

    try:
        # Save company goals
        create_company_goals(goals)

        # Start pipeline recalculation in background thread
        pipeline_thread = threading.Thread(target=_run_pipeline_thread, daemon=True)
        pipeline_thread.start()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Goals saved. Pipeline recalculation started.",
                    "goals_count": len(goals),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error saving goals: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/pipeline-status", methods=["GET"])
def get_pipeline_status():
    """Get current pipeline status."""
    return jsonify(pipeline_state), 200


@app.route("/api/employees", methods=["POST"])
def api_create_employee():
    """API endpoint to create a new employee and calculate recommendations."""

    data = request.get_json()

    try:
        job_role = data.get("jobRole", "").strip()
        job_level = int(data.get("jobLevel", 3))
        education = int(data.get("education", 3))
        performance = int(data.get("performance", 3))

        if not job_role:
            return jsonify({"error": "Job role is required"}), 400

        logger.info(f"=== Creating new employee ===")
        logger.info(
            f"JobRole: {job_role}, Level: {job_level}, Education: {education}, Performance: {performance}"
        )

        # Calculate skills
        logger.info("Step 1: Calculating current skills")
        current_skills = calculate_employee_skills(job_role, education, performance)
        logger.info(f"Current skills calculated: {len(current_skills)} skills")

        # Calculate target skills
        logger.info("Step 2: Calculating target skills")
        target_skills = calculate_target_skills(job_role)
        logger.info(f"Target skills calculated: {len(target_skills)} skills")

        # Calculate gap
        logger.info("Step 3: Calculating gap skills")
        gap_skills = calculate_gap_skills(current_skills, target_skills)
        non_zero_gaps = sum(1 for g in gap_skills.values() if float(g) > 0)
        logger.info(f"Gap skills calculated: {non_zero_gaps} non-zero gaps")

        # Get recommendations
        logger.info("Step 4: Generating course recommendations")
        recommendations = get_course_recommendations(job_role, job_level, gap_skills)
        logger.info(f"Recommendations generated: {len(recommendations)} courses")

        # Generate a new employee ID (numeric, based on max existing)
        try:
            # Get max ID from existing employees
            df_all = pd.read_csv(
                SKILL_MATRIX_CONFIGURATION["FINAL_SKILL_MATRIX_OUTPUT_PATH"]
            )
            max_existing_id = int(df_all["EmployeeNumber"].max())

            # Get max ID from existing employees
            import sqlite3
            from pathlib import Path as PathlibPath
            from scripts.employee_db import init_database

            init_database()
            db_path = PathlibPath(__file__).parent.parent / "config" / "database.db"
            max_temp_id = max_existing_id

            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT MAX(CAST(SUBSTR(id, 1) AS INTEGER)) FROM employees WHERE id NOT LIKE 'temp_%'"
                    )
                    result = cursor.fetchone()[0]
                    if result:
                        max_temp_id = max(max_temp_id, int(result))
            except Exception as e:
                logger.warning(f"Could not get max temp ID: {e}")

            employee_id = str(max_temp_id + 1)
            logger.info(f"Assigned new employee ID: {employee_id}")

        except Exception as e:
            logger.warning(f"Could not generate numeric ID, using temp: {e}")
            employee_id = f"temp_{int(pd.Timestamp.now().timestamp() * 1000)}"

        # Save to database
        logger.info(f"Step 5: Saving to database with ID {employee_id}")
        saved = save_employee(
            employee_id,
            job_role,
            job_level,
            education,
            performance,
            current_skills,
            target_skills,
            gap_skills,
            recommendations,
        )

        if not saved:
            logger.error("Failed to save employee to database")
            return jsonify({"error": "Failed to save employee"}), 500

        # Save gap_skills to gap_matrix table
        try:
            family = ROLE_TO_FAMILY.get(job_role, "unknown")
            save_gap_skills(employee_id, job_role, job_level, family, gap_skills)
            logger.info(f"Gap skills saved to gap_matrix for employee {employee_id}")
        except Exception as e:
            logger.warning(f"Could not save gap_skills to gap_matrix: {e}")

        logger.info(f"New employee successfully created: {employee_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "employee_id": employee_id,
                    "job_role": job_role,
                    "job_level": job_level,
                    "current_skills": current_skills,
                    "target_skills": target_skills,
                    "gap_skills": gap_skills,
                    "recommendations": recommendations,
                }
            ),
            200,
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating employee: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/employee/<emp_id>")
def employee_detail(emp_id):
    """Employee detail page with recommendations."""
    from scripts.employee_db import get_employee, get_gap_skills_from_matrix
    from scripts.employee_calculator import calculate_target_skills

    try:
        # Try to find in database employees first (works for numeric IDs)
        temp_emp = get_employee(emp_id)

        if temp_emp:
            # Found employee in database
            return render_template(
                "detail.html",
                emp_id=emp_id,
                emp_role=temp_emp["job_role"],
                emp_level=get_job_level_name(temp_emp["job_level"]),
                current_skills=[
                    {"skill": format_skill_name(skill), "score": float(score)}
                    for skill, score in temp_emp["current_skills"].items()
                ],
                target_skills=[],
                gap_skills=[
                    {"skill": format_skill_name(skill), "gap": float(gap_val)}
                    for skill, gap_val in temp_emp["gap_skills"].items()
                    if float(gap_val) > 0
                ],
                top_gap_skills=[
                    {"skill": format_skill_name(skill), "gap": float(gap_val)}
                    for skill, gap_val in sorted(
                        [
                            (s, g)
                            for s, g in temp_emp["gap_skills"].items()
                            if float(g) > 0
                        ],
                        key=lambda x: float(x[1]),
                        reverse=True,
                    )[:3]
                ],
                recommendations=[
                    {
                        "course_id": idx + 1,
                        "course_name": rec.get("course_title", "-"),
                        "subjects": ["Training"],
                        "skills": rec.get("skills", []),
                    }
                    for idx, rec in enumerate(temp_emp["recommendations"])
                ],
            )

        # Not found in database, search in CSV employees
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

        # Calculate target_skills on-the-fly for CSV employees
        try:
            target_skills_dict = calculate_target_skills(emp_role)
        except Exception as e:
            logger.warning(f"Could not calculate target skills for {emp_role}: {e}")
            target_skills_dict = {}

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
            current_skills=[
                {"skill": format_skill_name(col), "score": float(emp_row[col])}
                for col in SKILL_COLUMNS
                if col in emp_row.index and float(emp_row[col]) > 0
            ],
            target_skills=[],
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
