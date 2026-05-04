"""Prediction routes — single and batch."""

from datetime import datetime
from io import BytesIO

import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session

from backend.data.validator import (
    FarmInput,
    PredictionResponse,
    BatchPredictionResponse,
)
from backend.data.preprocessing import prepare_prediction_input
from backend.ml.pipeline import predict_with_confidence, ALL_PIPELINE_FEATURES
from backend.ml.explainability import generate_recommendations
from backend.api.database import get_db, PredictionRecord
from backend.api.routes.health import set_last_prediction_time
from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/predict", tags=["Predictions"])


def _classify_yield(value: float) -> str:
    """Bucket yield into high/medium/low."""
    if value > 3000:
        return "high"
    elif value > 1500:
        return "medium"
    else:
        return "low"


def _make_prediction(input_data: FarmInput, pipeline, explainer, db: Session) -> PredictionResponse:
    """Run one prediction through the pipeline and save to DB."""
    # Prepare input DataFrame
    input_dict = input_data.model_dump()
    df = prepare_prediction_input(input_dict)
    
    # Ensure columns match pipeline expectations
    for col in ALL_PIPELINE_FEATURES:
        if col not in df.columns:
            df[col] = 0
    df = df[ALL_PIPELINE_FEATURES]
    
    # Predict with confidence intervals
    predictions, lower, upper = predict_with_confidence(pipeline, df)
    
    predicted_yield = float(predictions[0])
    ci_lower = float(lower[0])
    ci_upper = float(upper[0])
    
    # SHAP explanation
    shap_values = {}
    if explainer:
        shap_values = explainer.explain_prediction(df)
    
    # Generate recommendations
    recommendations = generate_recommendations(input_dict, shap_values, predicted_yield)
    recommendation_text = " | ".join(recommendations)
    
    # Classify yield
    yield_category = _classify_yield(predicted_yield)
    
    # Store in database
    record = PredictionRecord(
        timestamp=datetime.utcnow(),
        farm_area=input_dict["farm_area"],
        temp_obs=input_dict["temp_obs"],
        wind_direction=input_dict["wind_direction"],
        dew_temp=input_dict["dew_temp"],
        pressure_sea_level=input_dict["pressure_sea_level"],
        precipitation=input_dict["precipitation"],
        wind_speed=input_dict["wind_speed"],
        unix_sec=input_dict["unix_sec"],
        ingredient_type=input_dict["ingredient_type"],
        farming_company=input_dict["farming_company"],
        deidentified_location=input_dict["deidentified_location"],
        num_processing_plants=input_dict["num_processing_plants"],
        predicted_yield=predicted_yield,
        confidence_lower=ci_lower,
        confidence_upper=ci_upper,
        yield_category=yield_category,
        model_version=settings.model_version,
        shap_values=shap_values,
        recommendation=recommendation_text,
    )
    db.add(record)
    db.commit()
    
    set_last_prediction_time()
    
    # Get feature importance from SHAP or model
    feature_importance = shap_values if shap_values else {}
    
    return PredictionResponse(
        predicted_yield=round(predicted_yield, 2),
        confidence_interval_lower=round(ci_lower, 2),
        confidence_interval_upper=round(ci_upper, 2),
        confidence_level=0.95,
        model_version=settings.model_version,
        prediction_timestamp=datetime.utcnow().isoformat(),
        feature_importance=feature_importance,
        shap_values=shap_values,
        recommendation=recommendation_text,
        yield_category=yield_category,
    )


@router.post("", response_model=PredictionResponse)
async def predict_single(input_data: FarmInput, db: Session = Depends(get_db)):
    """Run a single yield prediction."""
    from backend.api.main import get_model_pipeline, get_explainer
    
    pipeline = get_model_pipeline()
    explainer = get_explainer()
    
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first."
        )
    
    try:
        return _make_prediction(input_data, pipeline, explainer, db)
    except Exception as e:
        logger.error("prediction_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Predict on every row of an uploaded CSV."""
    from backend.api.main import get_model_pipeline, get_explainer
    
    pipeline = get_model_pipeline()
    explainer = get_explainer()
    
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first."
        )
    
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    try:
        content = await file.read()
        df = pd.read_csv(BytesIO(content))
        
        # Validate required columns
        required_cols = [
            "farm_area", "temp_obs", "wind_direction", "dew_temp",
            "pressure_sea_level", "precipitation", "wind_speed", "unix_sec",
            "ingredient_type", "farming_company", "deidentified_location",
            "num_processing_plants"
        ]
        
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing}"
            )
        
        predictions = []
        for _, row in df.iterrows():
            input_data = FarmInput(**row[required_cols].to_dict())
            pred = _make_prediction(input_data, pipeline, explainer, db)
            predictions.append(pred)
        
        # Summary statistics
        yields = [p.predicted_yield for p in predictions]
        summary = {
            "mean_yield": round(float(np.mean(yields)), 2),
            "median_yield": round(float(np.median(yields)), 2),
            "min_yield": round(float(np.min(yields)), 2),
            "max_yield": round(float(np.max(yields)), 2),
            "std_yield": round(float(np.std(yields)), 2),
            "high_yield_count": sum(1 for p in predictions if p.yield_category == "high"),
            "medium_yield_count": sum(1 for p in predictions if p.yield_category == "medium"),
            "low_yield_count": sum(1 for p in predictions if p.yield_category == "low"),
        }
        
        return BatchPredictionResponse(
            predictions=predictions,
            summary=summary,
            total_count=len(predictions)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("batch_prediction_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")
