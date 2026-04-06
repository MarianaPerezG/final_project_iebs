from rapidfuzz import fuzz
import logging
from typing import Dict, List, Tuple


class SkillMapper:

    def __init__(self, global_skills: List[str], threshold: float = 0.65):
        self.global_skills = global_skills
        self.threshold = threshold
        self.mapping_cache = {}
        self.unmapped_skills = []

    def _get_best_match(self, api_skill: str) -> Tuple[str, float]:
        best_match = None
        best_score = 0

        api_skill_lower = api_skill.lower().strip()

        for global_skill in self.global_skills:
            global_skill_lower = global_skill.lower()

            scores = [
                fuzz.ratio(api_skill_lower, global_skill_lower),
                fuzz.partial_ratio(api_skill_lower, global_skill_lower),
                fuzz.token_set_ratio(api_skill_lower, global_skill_lower),
                fuzz.token_sort_ratio(api_skill_lower, global_skill_lower),
            ]

            score = max(scores)

            if score > best_score:
                best_score = score
                best_match = global_skill

        return best_match, best_score / 100

    def map_skill(self, api_skill: str) -> str:
        if api_skill in self.mapping_cache:
            return self.mapping_cache[api_skill]

        best_match, confidence = self._get_best_match(api_skill)

        if confidence >= self.threshold:
            self.mapping_cache[api_skill] = best_match
            return best_match
        else:
            self.mapping_cache[api_skill] = None
            self.unmapped_skills.append((api_skill, best_match, confidence))
            return None

    def map_skills(self, api_skills: List[str]) -> List[str]:
        mapped = []
        for skill in api_skills:
            mapped_skill = self.map_skill(skill)
            if mapped_skill and mapped_skill not in mapped:
                mapped.append(mapped_skill)
        return mapped

    def get_mapping_report(self) -> Dict:
        return {
            "total_mappings": len(self.mapping_cache),
            "successful": len(
                [v for v in self.mapping_cache.values() if v is not None]
            ),
            "failed": len(self.unmapped_skills),
            "unmapped_skills": self.unmapped_skills,
            "mapping_cache": self.mapping_cache,
        }
