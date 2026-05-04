"""Data cleaning and feature prep — pure functions, no hardcoded paths."""

import pandas as pd
import numpy as np
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Feature definitions
NUMERIC_FEATURES = [
    "farm_area", "temp_obs", "wind_direction", "dew_temp",
    "pressure_sea_level", "precipitation", "wind_speed", "unix_sec"
]

CATEGORICAL_FEATURES = [
    "ingredient_type", "farming_company", "deidentified_location"
]

TARGET = "yield"

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES + ["num_processing_plants"]

PREDICTION_FEATURES = [
    "id", "farm_area", "temp_obs", "wind_direction", "dew_temp",
    "pressure_sea_level", "precipitation", "wind_speed", "unix_sec",
    "ingredient_type", "farming_company", "deidentified_location",
    "num_processing_plants"
]


def clean_train_data(train_data: pd.DataFrame) -> pd.DataFrame:
    """Parse dates, cast farm_id, drop dupes."""
    df = train_data.copy()
    
    # Convert date to datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    
    # Type conversion
    if "farm_id" in df.columns:
        df["farm_id"] = df["farm_id"].astype(str)
    
    # Drop duplicates
    initial_len = len(df)
    df = df.drop_duplicates(keep="first")
    dropped = initial_len - len(df)
    if dropped > 0:
        logger.info("duplicates_dropped", count=dropped)
    
    return df


def clean_farm_data(farm_data: pd.DataFrame) -> pd.DataFrame:
    """Drop unneeded cols, fill missing num_processing_plants."""
    df = farm_data.copy()
    
    # Drop operations_commencing_year if present
    if "operations_commencing_year" in df.columns:
        df = df.drop("operations_commencing_year", axis=1)
    
    # Type casting
    if "farm_id" in df.columns:
        df["farm_id"] = df["farm_id"].astype(str)
    
    # Fill missing num_processing_plants with median
    if "num_processing_plants" in df.columns:
        median_val = df["num_processing_plants"].median()
        df["num_processing_plants"] = df["num_processing_plants"].fillna(median_val)
        df["num_processing_plants"] = df["num_processing_plants"].astype(int)
    
    return df


def clean_weather_data(weather_data: pd.DataFrame) -> pd.DataFrame:
    """Parse timestamp, drop cloudiness."""
    df = weather_data.copy()
    
    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        )
    
    # Drop cloudiness if present
    if "cloudiness" in df.columns:
        df = df.drop("cloudiness", axis=1)
    
    return df


def merge_datasets(
    train_data: pd.DataFrame,
    farm_data: pd.DataFrame,
    weather_data: pd.DataFrame
) -> pd.DataFrame:
    """Join train + farm + weather into one training-ready table."""
    logger.info("merging_datasets")

    # ── 1. Merge train data with farm data on farm_id ──────────────────────
    # Drop farm-level columns from train_data that also exist in farm_data
    # (except farm_id itself which is the join key)
    farm_extra_cols = [
        c for c in farm_data.columns
        if c != "farm_id" and c in train_data.columns
    ]
    if farm_extra_cols:
        logger.info("dropping_duplicate_cols_from_train", cols=farm_extra_cols)
        train_data = train_data.drop(columns=farm_extra_cols)

    merged = pd.merge(train_data, farm_data, on="farm_id", how="left")

    # Rename date column to timestamp
    if "date" in merged.columns:
        merged = merged.rename(columns={"date": "timestamp"})

    # Drop deidentified_location from merged — it will come from weather
    if "deidentified_location" in merged.columns and "deidentified_location" in weather_data.columns:
        merged = merged.drop("deidentified_location", axis=1)

    # Drop operations_commencing_year if still present
    merged = merged.drop(
        columns=[c for c in ["operations_commencing_year"] if c in merged.columns]
    )

    # ── 2. Prepare weather data for merging ────────────────────────────────
    weather_copy = weather_data.copy()
    if "timestamp" in weather_copy.columns:
        weather_copy = weather_copy.drop("timestamp", axis=1)
    if "cloudiness" in weather_copy.columns:
        weather_copy = weather_copy.drop("cloudiness", axis=1)

    # Reset both indices to align on position
    merged = merged.reset_index(drop=True)
    # Truncate weather to match merged length
    weather_copy = weather_copy.reset_index(drop=True).iloc[:len(merged)]
    # If weather is shorter, pad with NaN (SimpleImputer will handle it)
    if len(weather_copy) < len(merged):
        pad = pd.DataFrame(
            np.nan, index=range(len(merged) - len(weather_copy)),
            columns=weather_copy.columns
        )
        weather_copy = pd.concat([weather_copy, pad], ignore_index=True)

    # ── 3. Concatenate weather features ────────────────────────────────────
    final = pd.concat([merged, weather_copy], axis=1)

    # ── 4. Drop farm_id (no longer needed) ────────────────────────────────
    if "farm_id" in final.columns:
        final = final.drop("farm_id", axis=1)

    # ── 5. Convert timestamp → unix_sec ────────────────────────────────────
    if "timestamp" in final.columns:
        final["unix_sec"] = (
            pd.to_datetime(final["timestamp"], errors="coerce").astype(np.int64) // 10**9
        )
        final = final.drop("timestamp", axis=1)

    if "Unix Sec" in final.columns:
        final = final.rename(columns={"Unix Sec": "unix_sec"})

    logger.info("datasets_merged", final_shape=final.shape)
    return final


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Label-encode categorical columns in place."""
    from sklearn.preprocessing import LabelEncoder
    
    result = df.copy()
    le = LabelEncoder()
    
    for col in CATEGORICAL_FEATURES:
        if col in result.columns and result[col].dtype == "object":
            result[col] = le.fit_transform(result[col].astype(str))
            result[col] = result[col].astype(int)
    
    return result


def prepare_training_data(
    train_data: pd.DataFrame,
    farm_data: pd.DataFrame,
    weather_data: pd.DataFrame
) -> tuple[pd.DataFrame, pd.Series]:
    """Full pipeline: clean → merge → encode → split X/y."""
    # Clean individual datasets
    train_clean = clean_train_data(train_data)
    farm_clean = clean_farm_data(farm_data)
    weather_clean = clean_weather_data(weather_data)
    
    # Merge
    merged = merge_datasets(train_clean, farm_clean, weather_clean)
    
    # Encode categoricals
    merged = encode_categoricals(merged)
    
    # Add ID column if not present
    if "id" not in merged.columns:
        merged.insert(0, "id", range(len(merged)))
    
    # Separate target
    if TARGET not in merged.columns:
        raise ValueError(f"Target column '{TARGET}' not found in merged data")
    
    y = merged[TARGET]
    X = merged.drop(columns=[TARGET])
    
    # Keep only expected features (in order)
    available_features = [f for f in PREDICTION_FEATURES if f in X.columns]
    X = X[available_features]
    
    logger.info(
        "training_data_prepared",
        X_shape=X.shape,
        y_shape=y.shape,
        features=list(X.columns)
    )
    
    return X, y


def prepare_prediction_input(input_data: dict) -> pd.DataFrame:
    """Dict → single-row DataFrame with correct column order."""
    # Build DataFrame with correct column order
    feature_order = [
        "farm_area", "temp_obs", "wind_direction", "dew_temp",
        "pressure_sea_level", "precipitation", "wind_speed", "unix_sec",
        "ingredient_type", "farming_company", "deidentified_location",
        "num_processing_plants"
    ]
    
    df = pd.DataFrame([input_data])[feature_order]
    return df
