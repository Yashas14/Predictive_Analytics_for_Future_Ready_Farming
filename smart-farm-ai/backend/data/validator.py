"""Pydantic request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FarmInput(BaseModel):
    """Single prediction input (all fields required)."""
    
    farm_area: float = Field(gt=0, description="Farm area in acres")
    temp_obs: float = Field(ge=-50, le=60, description="Temperature observation (°C)")
    wind_direction: float = Field(ge=0, le=360, description="Wind direction in degrees")
    dew_temp: float = Field(description="Dew point temperature (°C)")
    pressure_sea_level: float = Field(description="Sea level pressure (hPa)")
    precipitation: float = Field(ge=0, description="Precipitation (mm)")
    wind_speed: float = Field(ge=0, description="Wind speed (km/h)")
    unix_sec: int = Field(description="Unix timestamp in seconds")
    ingredient_type: int = Field(ge=0, le=10, description="Ingredient type code")
    farming_company: int = Field(ge=0, le=50, description="Farming company code")
    deidentified_location: int = Field(ge=0, le=100, description="Location code")
    num_processing_plants: int = Field(ge=1, description="Number of processing plants")

    class Config:
        json_schema_extra = {
            "example": {
                "farm_area": 150.5,
                "temp_obs": 25.3,
                "wind_direction": 180.0,
                "dew_temp": 12.5,
                "pressure_sea_level": 1013.25,
                "precipitation": 2.5,
                "wind_speed": 15.0,
                "unix_sec": 1646897931,
                "ingredient_type": 3,
                "farming_company": 12,
                "deidentified_location": 45,
                "num_processing_plants": 5
            }
        }


class BatchPredictionInput(BaseModel):
    predictions: list[FarmInput]


class PredictionResponse(BaseModel):
    """Shape of a prediction result."""
    
    predicted_yield: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence_level: float = 0.95
    model_version: str
    prediction_timestamp: str
    feature_importance: dict[str, float]
    shap_values: dict[str, float]
    recommendation: str
    yield_category: str  # "high", "medium", "low"


class BatchPredictionResponse(BaseModel):
    """Batch result with summary stats."""
    
    predictions: list[PredictionResponse]
    summary: dict
    total_count: int


class HealthResponse(BaseModel):
    """Health check payload."""
    
    status: str
    model_version: str
    uptime_seconds: float
    model_loaded: bool
    last_prediction: Optional[str] = None


class ModelMetrics(BaseModel):
    """Training + cross-validation metrics."""
    
    r2_score: float
    rmse: float
    mae: float
    cv_r2_mean: float
    cv_r2_std: float
    cv_rmse_mean: float
    cv_rmse_std: float
    training_date: str
    n_samples: int
    model_version: str


class FeatureImportanceResponse(BaseModel):
    """Ranked feature importances."""
    
    features: list[str]
    importances: list[float]
    model_type: str
