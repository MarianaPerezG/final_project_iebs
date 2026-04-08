JOB_LEVEL_MAPPING = {
    1: "Entry Level",
    2: "Mid Level",
    3: "Senior",
    4: "Lead",
    5: "Executive",
}

COURSE_LEVEL_MAPPING = {
    "beginner": 1,
    "intermediate-beginner": 2,
    "intermediate": 3,
    "intermediate-advanced": 4,
    "advanced": 5,
}


def get_job_level_name(level: int) -> str:
    return JOB_LEVEL_MAPPING.get(level, f"Level {level}")


def get_course_level_number(level_str: str) -> int:
    return COURSE_LEVEL_MAPPING.get(str(level_str).lower(), 3)
