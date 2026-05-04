"""Sklearn Pipeline: ColumnTransformer + VotingRegressor ensemble."""

import pickle
import json
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer

from backend.ml.models.ensemble import get_ensemble
from backend.data.preprocessing import NUMERIC_FEATURES, CATEGORICAL_FEATURES
from backend.utils.logger import get_logger
from backend.utils.config import settings

logger = get_logger(__name__)

# Feature lists (must match training order)
PIPELINE_NUMERIC_FEATURES = [
    "farm_area", "temp_obs", "wind_direction", "dew_temp",
    "pressure_sea_level", "precipitation", "wind_speed", "unix_sec",
    "num_processing_plants"
]

PIPELINE_CATEGORICAL_FEATURES = [
    "ingredient_type", "farming_company", "deidentified_location"
]

ALL_PIPELINE_FEATURES = PIPELINE_NUMERIC_FEATURES + PIPELINE_CATEGORICAL_FEATURES


def build_preprocessor() -> ColumnTransformer:
    """Impute + scale numerics; impute + ordinal-encode categoricals."""
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, PIPELINE_NUMERIC_FEATURES),
            ("cat", categorical_transformer, PIPELINE_CATEGORICAL_FEATURES)
        ],
        remainder="drop"
    )

    return preprocessor


def build_pipeline(random_state: int = 42) -> Pipeline:
    """Assemble preprocessor + voting ensemble into a single Pipeline."""
    preprocessor = build_preprocessor()
    ensemble = get_ensemble(random_state=random_state)

    full_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", ensemble)
    ])

    logger.info("pipeline_built", features=ALL_PIPELINE_FEATURES)
    return full_pipeline


def save_pipeline(
    pipeline: Pipeline,
    metrics: dict,
    feature_names: list[str],
    save_dir: Path | None = None,
    version: str | None = None
) -> Path:
    """Pickle the pipeline and write metadata JSON alongside it."""
    version = version or settings.model_version
    save_dir = save_dir or (settings.project_root / "models" / f"v{version.replace('.', '_')}")
    save_dir.mkdir(parents=True, exist_ok=True)

    # Save model
    model_path = save_dir / "model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)

    # Save metadata
    metadata = {
        "model_version": version,
        "training_date": datetime.now().isoformat(),
        "feature_names": feature_names,
        "metrics": metrics,
        "pipeline_steps": [step[0] for step in pipeline.steps],
        "model_type": "VotingRegressor(RF+XGBoost+LightGBM)",
    }

    metadata_path = save_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    logger.info("pipeline_saved", path=str(model_path), version=version)
    return model_path


def load_pipeline(model_path: Path | None = None) -> Pipeline:
    """Unpickle a previously saved pipeline."""
    model_path = model_path or settings.abs_model_path

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at: {model_path}")

    with open(model_path, "rb") as f:
        pipeline = pickle.load(f)

    logger.info("pipeline_loaded", path=str(model_path))
    return pipeline


def load_metadata(model_dir: Path | None = None) -> dict:
    """Read metadata.json next to the model pickle."""
    if model_dir is None:
        model_dir = settings.abs_model_path.parent

    metadata_path = model_dir / "metadata.json"
    if not metadata_path.exists():
        return {"model_version": settings.model_version, "metrics": {}}

    with open(metadata_path, "r") as f:
        return json.load(f)


def predict_with_confidence(
    pipeline: Pipeline,
    X: pd.DataFrame,
    confidence: float = 0.95
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Predict + derive confidence intervals from model disagreement.

    Returns (mean_predictions, lower_bound, upper_bound).
    """
    # Get predictions from the ensemble
    predictions = pipeline.predict(X)

    # Access individual model predictions for confidence intervals
    preprocessor = pipeline.named_steps["preprocessor"]
    X_transformed = preprocessor.transform(X)

    model = pipeline.named_steps["model"]
    individual_predictions = []

    for estimator in model.estimators_:
        pred = estimator.predict(X_transformed)
        individual_predictions.append(pred)

    individual_predictions = np.array(individual_predictions)

    # Calculate confidence intervals from model disagreement
    std = np.std(individual_predictions, axis=0)
    z_score = 1.96 if confidence == 0.95 else 1.645  # 95% or 90% CI

    lower = predictions - z_score * std
    upper = predictions + z_score * std

    return predictions, lower, upper
