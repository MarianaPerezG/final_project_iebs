import re
from typing import List


class SkillNormalizer:

    @staticmethod
    def normalize(skill: str) -> str:
        skill = skill.lower().strip()

        abbreviations = {
            r"\bml\b": "machine learning",
            r"\bai\b": "artificial intelligence",
            r"\bapi\b": "api",
            r"\bdb\b": "database",
            r"\bvcs\b": "version control",
            r"\bci/cd\b": "continuous integration",
            r"\bdev ops\b": "devops",
        }

        for abbr, full in abbreviations.items():
            skill = re.sub(abbr, full, skill)

        skill = re.sub(r"[^\w\s+#]", "", skill)
        skill = re.sub(r"\s+", " ", skill).strip()

        return skill
