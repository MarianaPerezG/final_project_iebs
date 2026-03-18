from src.pipelines.run_pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline(dataset_path="data/raw/ibm_hr.csv")

    print(result.matrix.head())
