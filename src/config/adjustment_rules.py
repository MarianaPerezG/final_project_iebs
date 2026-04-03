from config.global_skills import GLOBAL_SKILLS

LOW_WEIGHT = 0.10
HIGH_WEIGHT = 0.20

MIN_EDUCATION = 1
MAX_EDUCATION = 5

MIN_PERFORMANCE = 1
MAX_PERFORMANCE = 5

SOFT_SKILLS = {
    "collaboration",
    "leadership",
    "business_functions",
    "project_management",
}

HARD_SKILLS = {
    "analytics",
    "software_data",
    "systems",
    "domain_expertise",
}

if SOFT_SKILLS & HARD_SKILLS:
    raise ValueError(
        f"duplicated skills across groups: {sorted(SOFT_SKILLS & HARD_SKILLS)}"
    )

if (SOFT_SKILLS | HARD_SKILLS) != set(GLOBAL_SKILLS):
    missing = sorted(set(GLOBAL_SKILLS) - (SOFT_SKILLS | HARD_SKILLS))
    unexpected = sorted((SOFT_SKILLS | HARD_SKILLS) - set(GLOBAL_SKILLS))
    raise ValueError(
        f"skill grouping mismatch | missing: {missing} | unexpected: {unexpected}"
    )
