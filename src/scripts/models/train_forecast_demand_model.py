from pathlib import Path
from venv import logger
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.config.datasets import TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION


def train_forecast_demand_model() -> None:

    data_path = Path(TARGET_DEMAND_SKILL_MATRIX_CONFIGURATION["DATASET_PATH"])
    existing_csvs = list(data_path.rglob("*.csv"))
    if not existing_csvs:
        logger.info(f"Dataset not found at {data_path}. Please download it first.")
        return

    df = pd.read_csv(existing_csvs[0])

    X = df["year", "ibm_role"]
    y = df["demand"]

    model = LinearRegression()
    model.fit(X, y)

    model_path = Path("models/forecast_demand_model.joblib")
    joblib.dump(model, model_path)


def create_year_column(df: pd.DataFrame) -> pd.DataFrame:
    df["year"] = pd.to_datetime(df["date"]).dt.year
    return df


def create_demand_column(df: pd.DataFrame) -> pd.DataFrame:
    # Tenemos que mappear a los roles de ibm, y luego sumar la cantidad de cada rol por año
    ROLE_TO_FAMILY = {}
    df["ibm_role"] = df["role"].map(ROLE_TO_FAMILY)
    df = df.groupby(["year", "ibm_role"]).size().reset_index(name="demand")
    return df
