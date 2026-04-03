from config.global_skills import GLOBAL_SKILLS


def _score(**skills: int) -> dict[str, int]:
    unknown_skills = sorted(set(skills) - set(GLOBAL_SKILLS))
    if unknown_skills:
        raise ValueError(f"unknown skills: {unknown_skills}")

    return {skill: skills.get(skill, 0) for skill in GLOBAL_SKILLS}


MIN_SKILL_SCORE = 0
MAX_SKILL_SCORE = 5

ROLE_TO_FAMILY = {
    "Human Resources": "corporate_services",
    "Healthcare Representative": "client_partnerships",
    "Sales Executive": "client_partnerships",
    "Sales Representative": "client_partnerships",
    "Laboratory Technician": "specialized_technical_services",
    "Research Director": "research_development",
    "Research Scientist": "research_development",
    "Manager": "business_operations",
    "Manufacturing Director": "business_operations",
}

FAMILY_SCORES = {
    "corporate_services": _score(
        collaboration=4,
        leadership=3,
        business_functions=5,
        analytics=2,
        project_management=3,
    ),
    "client_partnerships": _score(
        collaboration=4,
        leadership=1,
        business_functions=5,
        analytics=1,
        project_management=2,
        domain_expertise=1,
    ),
    "specialized_technical_services": _score(
        collaboration=2,
        analytics=2,
        project_management=1,
        systems=1,
        domain_expertise=5,
    ),
    "research_development": _score(
        collaboration=3,
        leadership=2,
        analytics=5,
        project_management=2,
        software_data=1,
        domain_expertise=5,
    ),
    "business_operations": _score(
        collaboration=4,
        leadership=3,
        business_functions=1,
        analytics=2,
        project_management=5,
        systems=2,
        domain_expertise=1,
    ),
}

SEMANTIC_ADJUSTMENTS = {
    "Director": _score(
        collaboration=1,
        leadership=2,
        project_management=1,
    ),
    "Manager": _score(
        leadership=1,
        project_management=1,
    ),
    "Executive": _score(
        leadership=1,
        project_management=1,
    ),
    "Sales": _score(
        business_functions=1,
    ),
    "Representative": _score(
        collaboration=1,
    ),
    "Research": _score(
        analytics=1,
    ),
    "Scientist": _score(
        domain_expertise=1,
    ),
    "Healthcare": _score(
        domain_expertise=1,
    ),
    "Laboratory": _score(
        systems=1,
        domain_expertise=1,
    ),
    "Technician": _score(
        leadership=-1,
        domain_expertise=1,
    ),
    "Manufacturing": _score(
        systems=1,
        domain_expertise=1,
    ),
}
