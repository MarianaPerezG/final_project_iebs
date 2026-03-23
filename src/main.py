from pathlib import Path

from schemas import DownloadConfig
from scripts.download_data import download_kaggle_dataset
from scripts.pipelines import run_pipeline

if __name__ == "__main__":
    
    SKILL_MATRIX_DATASET_REF = "marianaprezgonzlez/ibm-hr-analytics-employee-attrition-and-performance"
    SIKLL_MATRIX_OUTPUT_PATH = "src/data/raw/skill_matrix.csv"
    
    dataset_path = Path(SIKLL_MATRIX_OUTPUT_PATH)
    if not dataset_path.exists():   
        download_kaggle_dataset(DownloadConfig(dataset_ref=SKILL_MATRIX_DATASET_REF), output_path=SIKLL_MATRIX_OUTPUT_PATH)
    else:
        print(f"Dataset already exists at {dataset_path}, skipping download.")
            
    result = run_pipeline(dataset_path=SIKLL_MATRIX_OUTPUT_PATH)

    print(result.matrix.head())
