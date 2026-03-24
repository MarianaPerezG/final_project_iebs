
from data.global_skills import GLOBAL_SKILLS
from scripts.pipelines import run_pipeline
from skill_matrix.configuration import create_skill_matrixconfig


if __name__ == "__main__":
         
   run_pipeline(global_skills=GLOBAL_SKILLS, skill_matrix_config=create_skill_matrixconfig())
    
