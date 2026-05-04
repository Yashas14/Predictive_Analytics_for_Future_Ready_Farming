"""API endpoint tests."""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        """Health endpoint should return 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    def test_health_response_structure(self, client):
        """Health response should have required fields."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert "status" in data
        assert "model_version" in data
        assert "uptime_seconds" in data
        assert "model_loaded" in data
    
    def test_health_uptime_positive(self, client):
        """Uptime should be a positive number."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["uptime_seconds"] >= 0


class TestPredictEndpoint:
    @pytest.fixture
    def valid_input(self):
        """Valid prediction input data."""
        return {
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
    
    def test_predict_valid_input(self, client, valid_input):
        """Valid input should return a prediction (or 503 if model not loaded)."""
        response = client.post("/api/v1/predict", json=valid_input)
        # Either prediction succeeds or model not loaded
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "predicted_yield" in data
            assert "confidence_interval_lower" in data
            assert "confidence_interval_upper" in data
            assert "yield_category" in data
            assert data["yield_category"] in ["high", "medium", "low"]
    
    def test_predict_invalid_farm_area(self, client, valid_input):
        """Negative farm area should return 422."""
        valid_input["farm_area"] = -10.0
        response = client.post("/api/v1/predict", json=valid_input)
        assert response.status_code == 422
    
    def test_predict_invalid_temp(self, client, valid_input):
        """Temperature out of range should return 422."""
        valid_input["temp_obs"] = 100.0  # > 60
        response = client.post("/api/v1/predict", json=valid_input)
        assert response.status_code == 422
    
    def test_predict_invalid_wind_direction(self, client, valid_input):
        """Wind direction > 360 should return 422."""
        valid_input["wind_direction"] = 400.0
        response = client.post("/api/v1/predict", json=valid_input)
        assert response.status_code == 422
    
    def test_predict_missing_field(self, client, valid_input):
        """Missing required field should return 422."""
        del valid_input["farm_area"]
        response = client.post("/api/v1/predict", json=valid_input)
        assert response.status_code == 422
    
    def test_predict_negative_precipitation(self, client, valid_input):
        """Negative precipitation should return 422."""
        valid_input["precipitation"] = -1.0
        response = client.post("/api/v1/predict", json=valid_input)
        assert response.status_code == 422


class TestBatchPredictEndpoint:
    def test_batch_predict_csv(self, client, tmp_path):
        """Batch prediction with valid CSV."""
        csv_content = (
            "farm_area,temp_obs,wind_direction,dew_temp,pressure_sea_level,"
            "precipitation,wind_speed,unix_sec,ingredient_type,farming_company,"
            "deidentified_location,num_processing_plants\n"
            "150.0,25.0,180.0,12.0,1013.25,5.0,15.0,1646897931,3,12,45,5\n"
            "200.0,30.0,90.0,15.0,1010.0,0.0,8.0,1646984331,5,8,22,3\n"
        )
        
        response = client.post(
            "/api/v1/predict/batch",
            files={"file": ("test.csv", csv_content.encode(), "text/csv")}
        )
        # Either success or model not loaded
        assert response.status_code in [200, 503]
    
    def test_batch_predict_invalid_file_type(self, client):
        """Non-CSV file should return 400."""
        response = client.post(
            "/api/v1/predict/batch",
            files={"file": ("test.txt", b"some text", "text/plain")}
        )
        assert response.status_code == 400


class TestAnalyticsEndpoints:
    def test_feature_importance(self, client):
        """Feature importance endpoint should return data."""
        response = client.get("/api/v1/analytics/feature-importance")
        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert "importances" in data
    
    def test_model_metrics(self, client):
        """Model metrics endpoint should return metrics."""
        response = client.get("/api/v1/analytics/model-metrics")
        assert response.status_code == 200
        data = response.json()
        assert "r2_score" in data
        assert "rmse" in data
        assert "mae" in data
    
    def test_historical_predictions(self, client):
        """Historical predictions endpoint should return data."""
        response = client.get("/api/v1/analytics/historical-predictions?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "total" in data
    
    def test_model_comparison(self, client):
        """Model comparison endpoint should return data."""
        response = client.get("/api/v1/analytics/model-comparison")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root(self, client):
        """Root endpoint should return 200 (serves frontend or API info)."""
        response = client.get("/")
        assert response.status_code == 200
