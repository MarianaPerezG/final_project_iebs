DATASETS_CONFIGURATION = {
    "SKILL_MATRIX_DATASET_REF": "marianaprezgonzlez/ibm-hr-analytics-employee-attrition-and-performance",
    "SKILL_MATRIX_OUTPUT_PATH": "data/raw/skill_matrix.csv",
    "TARGET_DEMAND_SKILL_MATRIX_DATASET_REF": "marianaprezgonzlez/linkedin-job-postings-2023-2024",
    "TARGET_DEMAND_SKILL_MATRIX_OUTPUT_PATH": "data/raw/target_demand_skill_matrix.csv",
    "COURSE_RECOMMENDATION_DATASET_REF": "marianaprezgonzlez/multi-platform-online-courses-dataset",
    "COURSE_RECOMMENDATION_OUTPUT_PATH": "data/raw/course_recommendation.csv",
}

SKILL_MATRIX_CONFIGURATION = {
    "DATASET_PATH": DATASETS_CONFIGURATION["SKILL_MATRIX_OUTPUT_PATH"],
    "FINAL_SKILL_MATRIX_OUTPUT_PATH": "data/final/skill_matrix_result.csv",
}

TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION = {
    "DATASET_PATH": DATASETS_CONFIGURATION["TARGET_DEMAND_SKILL_MATRIX_OUTPUT_PATH"],
    "MAPPED_OUTPUT_PATH": "data/processed/target_demand_skill_matrix_result.csv",
    "SKILL_DEMAND_OUTPUT_PATH": "data/processed/skill_demand_vector.csv",
}

TARGET_COMPANY_GOALS_MATRIX_CONFIGURATION = {
    "GOALS_OUTPUT_PATH": "data/processed/company_goals_vector.csv",
}

TARGET_MATRIX_CONFIGURATION = {
    "SKILL_MATRIX_PATH": SKILL_MATRIX_CONFIGURATION["FINAL_SKILL_MATRIX_OUTPUT_PATH"],
    "SKILL_DEMAND_PATH": TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION[
        "SKILL_DEMAND_OUTPUT_PATH"
    ],
    "FINAL_TARGET_MATRIX_OUTPUT_PATH": "data/final/target_matrix_result.csv",
}

RECOMMENDATION_MATRIX_CONFIGURATION = {
    "FINAL_RECOMMENDATION_MATRIX_OUTPUT_PATH": "data/final/course_skills_matrix.csv",
    "UNMAPPED_SKILLS_REPORT_PATH": "data/reports/unmapped_skills.json",
}

COURSE_RECOMMENDATIONS_CONFIGURATION = {
    "GAP_MATRIX_PATH": "data/final/gap_matrix_result.csv",
    "COURSE_MATRIX_PATH": "data/final/course_skills_matrix.csv",
    "MODEL_PATH": "models/trained/course_recommendations_model.pkl",
    "CURRENT_EMPLOYEES_RECOMMENDATIONS_PATH": "data/final/course_recommendations.csv",
}
