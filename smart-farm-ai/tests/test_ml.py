"""ML pipeline and model tests."""

import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ml.pipeline import (
    build_pipeline,
    build_preprocessor,
    ALL_PIPELINE_FEATURES,
    PIPELINE_NUMERIC_FEATURES,
    PIPELINE_CATEGORICAL_FEATURES,
)
from backend.ml.evaluation import evaluate_model, get_feature_importance
from backend.ml.models.ensemble import get_ensemble, get_individual_models
from backend.ml.models.random_forest import get_random_forest
from backend.ml.models.xgboost_model import get_xgboost
from backend.ml.models.lightgbm_model import get_lightgbm
from backend.data.validator import FarmInput
from backend.data.preprocessing import prepare_prediction_input


@pytest.fixture
def sample_data():
    """Generate sample training data."""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        "farm_area": np.random.uniform(10, 500, n_samples),
        "temp_obs": np.random.uniform(-10, 45, n_samples),
        "wind_direction": np.random.uniform(0, 360, n_samples),
        "dew_temp": np.random.uniform(-20, 30, n_samples),
        "pressure_sea_level": np.random.uniform(990, 1030, n_samples),
        "precipitation": np.random.uniform(0, 50, n_samples),
        "wind_speed": np.random.uniform(0, 80, n_samples),
        "unix_sec": np.random.randint(1600000000, 1700000000, n_samples),
        "num_processing_plants": np.random.randint(1, 20, n_samples),
        "ingredient_type": np.random.randint(0, 10, n_samples),
        "farming_company": np.random.randint(0, 40, n_samples),
        "deidentified_location": np.random.randint(0, 80, n_samples),
    }
    
    X = pd.DataFrame(data)
    y = pd.Series(
        np.random.uniform(500, 5000, n_samples),
        name="yield"
    )
    
    return X, y


class TestPipeline:
    def test_build_pipeline(self):
        """Pipeline should build without errors."""
        pipeline = build_pipeline()
        assert pipeline is not None
        assert "preprocessor" in pipeline.named_steps
        assert "model" in pipeline.named_steps
    
    def test_pipeline_fit_predict(self, sample_data):
        """Pipeline should fit and predict without errors."""
        X, y = sample_data
        pipeline = build_pipeline()
        
        pipeline.fit(X, y)
        predictions = pipeline.predict(X)
        
        assert predictions is not None
        assert len(predictions) == len(X)
        assert all(np.isfinite(predictions))
    
    def test_pipeline_prediction_shape(self, sample_data):
        """Predictions should have correct shape."""
        X, y = sample_data
        pipeline = build_pipeline()
        pipeline.fit(X, y)
        
        # Single prediction
        single_pred = pipeline.predict(X.iloc[[0]])
        assert single_pred.shape == (1,)
        
        # Batch prediction
        batch_pred = pipeline.predict(X.iloc[:10])
        assert batch_pred.shape == (10,)
    
    def test_preprocessor_columns(self):
        """Preprocessor should handle expected features."""
        preprocessor = build_preprocessor()
        
        assert preprocessor is not None
        transformer_names = [t[0] for t in preprocessor.transformers]
        assert "num" in transformer_names
        assert "cat" in transformer_names


class TestModels:
    def test_random_forest_creation(self):
        """Random forest should be created with correct params."""
        rf = get_random_forest()
        assert rf.n_estimators == 200
        assert rf.max_depth == 20
        assert rf.random_state == 42
    
    def test_xgboost_creation(self):
        """XGBoost should be created with correct params."""
        xgb = get_xgboost()
        assert xgb.n_estimators == 200
        assert xgb.learning_rate == 0.05
        assert xgb.random_state == 42
    
    def test_lightgbm_creation(self):
        """LightGBM should be created with correct params."""
        lgb = get_lightgbm()
        assert lgb.n_estimators == 200
        assert lgb.learning_rate == 0.05
        assert lgb.random_state == 42
    
    def test_ensemble_creation(self):
        """Ensemble should combine all models."""
        ensemble = get_ensemble()
        assert len(ensemble.estimators) == 3
        
        names = [e[0] for e in ensemble.estimators]
        assert "rf" in names
        assert "xgb" in names
        assert "lgb" in names
    
    def test_individual_models_dict(self):
        """Individual models dict should have all models."""
        models = get_individual_models()
        assert "random_forest" in models
        assert "xgboost" in models
        assert "lightgbm" in models


class TestEvaluation:
    """Tests for evaluation metrics."""
    
    def test_evaluate_model(self):
        """Evaluation should return all expected metrics."""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 2.2, 2.9, 4.1, 5.2])
        
        metrics = evaluate_model(y_true, y_pred)
        
        assert "r2_score" in metrics
        assert "rmse" in metrics
        assert "mae" in metrics
        assert "mse" in metrics
        assert metrics["r2_score"] > 0.9  # Should be good fit
        assert metrics["rmse"] < 0.5
    
    def test_feature_importance_shape(self, sample_data):
        """Feature importance should match number of features."""
        X, y = sample_data
        pipeline = build_pipeline()
        pipeline.fit(X, y)
        
        importance = get_feature_importance(pipeline, ALL_PIPELINE_FEATURES)
        
        assert len(importance) == len(ALL_PIPELINE_FEATURES)
        assert all(v >= 0 for v in importance.values())
        # Should sum approximately to 1
        assert abs(sum(importance.values()) - 1.0) < 0.01


class TestShapExplainability:
    """Tests for SHAP explainability."""
    
    def test_shap_values_generated(self, sample_data):
        """SHAP values should be generated for a prediction."""
        from backend.ml.explainability import ModelExplainer
        
        X, y = sample_data
        pipeline = build_pipeline()
        pipeline.fit(X, y)
        
        explainer = ModelExplainer(pipeline, ALL_PIPELINE_FEATURES)
        shap_values = explainer.explain_prediction(X.iloc[[0]])
        
        assert shap_values is not None
        assert isinstance(shap_values, dict)
        assert len(shap_values) > 0
    
    def test_shap_batch_explanation(self, sample_data):
        """Batch SHAP should return values for each row."""
        from backend.ml.explainability import ModelExplainer
        
        X, y = sample_data
        pipeline = build_pipeline()
        pipeline.fit(X, y)
        
        explainer = ModelExplainer(pipeline, ALL_PIPELINE_FEATURES)
        batch_shap = explainer.explain_batch(X.iloc[:5])
        
        assert len(batch_shap) == 5
        for sv in batch_shap:
            assert isinstance(sv, dict)


class TestValidation:
    """Tests for input validation."""
    
    def test_valid_farm_input(self):
        """Valid input should pass validation."""
        input_data = FarmInput(
            farm_area=150.0,
            temp_obs=25.0,
            wind_direction=180.0,
            dew_temp=12.0,
            pressure_sea_level=1013.25,
            precipitation=5.0,
            wind_speed=15.0,
            unix_sec=1646897931,
            ingredient_type=3,
            farming_company=12,
            deidentified_location=45,
            num_processing_plants=5
        )
        assert input_data.farm_area == 150.0
    
    def test_invalid_farm_area_zero(self):
        """Farm area of 0 should fail validation."""
        with pytest.raises(Exception):
            FarmInput(
                farm_area=0,
                temp_obs=25.0,
                wind_direction=180.0,
                dew_temp=12.0,
                pressure_sea_level=1013.25,
                precipitation=5.0,
                wind_speed=15.0,
                unix_sec=1646897931,
                ingredient_type=3,
                farming_company=12,
                deidentified_location=45,
                num_processing_plants=5
            )
    
    def test_prepare_prediction_input(self):
        """Prepare prediction input should return correct DataFrame."""
        input_dict = {
            "farm_area": 150.0,
            "temp_obs": 25.0,
            "wind_direction": 180.0,
            "dew_temp": 12.0,
            "pressure_sea_level": 1013.25,
            "precipitation": 5.0,
            "wind_speed": 15.0,
            "unix_sec": 1646897931,
            "ingredient_type": 3,
            "farming_company": 12,
            "deidentified_location": 45,
            "num_processing_plants": 5
        }
        
        df = prepare_prediction_input(input_dict)
        
        assert len(df) == 1
        assert "farm_area" in df.columns
        assert df.iloc[0]["farm_area"] == 150.0
