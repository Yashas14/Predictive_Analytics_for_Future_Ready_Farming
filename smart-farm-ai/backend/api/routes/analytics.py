"""Analytics routes — feature importance, metrics, history."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.data.validator import FeatureImportanceResponse, ModelMetrics
from backend.ml.pipeline import load_metadata, ALL_PIPELINE_FEATURES
from backend.ml.evaluation import get_feature_importance
from backend.api.database import get_db, PredictionRecord
from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/feature-importance", response_model=FeatureImportanceResponse)
async def get_feature_importance_endpoint():
    """Return ranked feature importances from the trained model."""
    from backend.api.main import get_model_pipeline
    
    pipeline = get_model_pipeline()
    if pipeline is None:
        # Return from metadata
        metadata = load_metadata()
        fi = metadata.get("metrics", {}).get("feature_importance", {})
        if fi:
            return FeatureImportanceResponse(
                features=list(fi.keys()),
                importances=list(fi.values()),
                model_type="ensemble"
            )
        return FeatureImportanceResponse(
            features=ALL_PIPELINE_FEATURES,
            importances=[1.0 / len(ALL_PIPELINE_FEATURES)] * len(ALL_PIPELINE_FEATURES),
            model_type="unknown"
        )
    
    importance = get_feature_importance(pipeline, ALL_PIPELINE_FEATURES)
    
    return FeatureImportanceResponse(
        features=list(importance.keys()),
        importances=list(importance.values()),
        model_type="VotingRegressor(RF+XGB+LGBM)"
    )


@router.get("/model-metrics", response_model=ModelMetrics)
async def get_model_metrics():
    """Return test-set and cross-validation metrics."""
    metadata = load_metadata()
    metrics = metadata.get("metrics", {})
    test_metrics = metrics.get("test", {})
    cv_metrics = metrics.get("cross_validation", {})
    
    return ModelMetrics(
        r2_score=test_metrics.get("r2_score", 0.0),
        rmse=test_metrics.get("rmse", 0.0),
        mae=test_metrics.get("mae", 0.0),
        cv_r2_mean=cv_metrics.get("cv_r2_mean", 0.0),
        cv_r2_std=cv_metrics.get("cv_r2_std", 0.0),
        cv_rmse_mean=cv_metrics.get("cv_rmse_mean", 0.0),
        cv_rmse_std=cv_metrics.get("cv_rmse_std", 0.0),
        training_date=metadata.get("training_date", "N/A"),
        n_samples=metrics.get("n_train_samples", 0) + metrics.get("n_test_samples", 0),
        model_version=metadata.get("model_version", settings.model_version)
    )


@router.get("/historical-predictions")
async def get_historical_predictions(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Paginated list of past predictions."""
    records = (
        db.query(PredictionRecord)
        .order_by(desc(PredictionRecord.timestamp))
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    total = db.query(PredictionRecord).count()
    
    history = []
    for r in records:
        history.append({
            "id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "predicted_yield": r.predicted_yield,
            "confidence_lower": r.confidence_lower,
            "confidence_upper": r.confidence_upper,
            "yield_category": r.yield_category,
            "farm_area": r.farm_area,
            "temp_obs": r.temp_obs,
            "ingredient_type": r.ingredient_type,
            "farming_company": r.farming_company,
            "deidentified_location": r.deidentified_location,
            "model_version": r.model_version,
        })
    
    return {
        "predictions": history,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/model-comparison")
async def get_model_comparison():
    """Side-by-side metrics for each sub-model in the ensemble."""
    metadata = load_metadata()
    metrics = metadata.get("metrics", {})
    comparison = metrics.get("model_comparison", [])
    
    if not comparison:
        # Return default comparison structure
        return {
            "models": [
                {"model": "random_forest", "test_r2": 0, "test_rmse": 0, "test_mae": 0},
                {"model": "xgboost", "test_r2": 0, "test_rmse": 0, "test_mae": 0},
                {"model": "lightgbm", "test_r2": 0, "test_rmse": 0, "test_mae": 0},
            ]
        }
    
    return {"models": comparison}
