from config.dummy_goals import COMPANY_GOALS
from config.global_skills import GLOBAL_SKILLS


def get_company_goals() -> dict[str, int]:
    return {skill: int(COMPANY_GOALS.get(skill, 0)) for skill in GLOBAL_SKILLS}
