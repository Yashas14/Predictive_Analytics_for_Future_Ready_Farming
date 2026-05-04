# 🌾 AgriSense AI — Next-Gen Yield Intelligence Platform

<div align="center">

```
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     🌾  A G R I S E N S E   A I  🌾                     ║
    ║                                                           ║
    ║     Next-Generation Agricultural Yield Intelligence       ║
    ║     Powered by Ensemble ML + SHAP Explainability         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
```

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.34-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-BAFF29)](LICENSE)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)

</div>

---

## 📋 Problem Statement

Agricultural yield prediction is critical for food security, supply chain planning, and farm economics. Traditional approaches rely on simplistic models or manual estimation, leading to:

- **Inaccurate forecasts** that disrupt supply chains
- **No explainability** — farmers don't know *why* predictions change
- **No real-time adaptability** to weather conditions
- **No confidence intervals** — point estimates are unreliable

**AgriSense AI** solves this with a production-grade ensemble ML system that provides accurate, explainable, and actionable yield predictions.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGRISENSE AI                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    HTTP/JSON    ┌──────────────────────────┐  │
│  │              │  ◄────────────► │                          │  │
│  │   STREAMLIT  │                 │       FASTAPI            │  │
│  │   FRONTEND   │                 │       BACKEND            │  │
│  │              │                 │                          │  │
│  │  • Dashboard │                 │  • /predict              │  │
│  │  • Predictor │                 │  • /predict/batch        │  │
│  │  • Analytics │                 │  • /analytics/*          │  │
│  │  • Batch     │                 │  • /data/upload          │  │
│  │  • History   │                 │  • /health               │  │
│  │              │                 │                          │  │
│  └──────────────┘                 └──────────┬───────────────┘  │
│                                              │                   │
│                                    ┌─────────▼──────────┐       │
│                                    │                    │        │
│                                    │    ML ENGINE       │        │
│                                    │                    │        │
│                                    │  ┌──────────────┐ │        │
│                                    │  │ Preprocessor │ │        │
│                                    │  └──────┬───────┘ │        │
│                                    │         ▼         │        │
│                                    │  ┌──────────────┐ │        │
│                                    │  │   Ensemble   │ │        │
│                                    │  │  RF+XGB+LGB  │ │        │
│                                    │  └──────┬───────┘ │        │
│                                    │         ▼         │        │
│                                    │  ┌──────────────┐ │        │
│                                    │  │    SHAP      │ │        │
│                                    │  │ Explainer    │ │        │
│                                    │  └──────────────┘ │        │
│                                    │                    │        │
│                                    └────────────────────┘        │
│                                              │                   │
│                                    ┌─────────▼──────────┐       │
│                                    │   SQLite DB        │       │
│                                    │  (Predictions)     │       │
│                                    └────────────────────┘        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Ensemble ML** | VotingRegressor combining RandomForest + XGBoost + LightGBM |
| 🔍 **SHAP Explainability** | Every prediction comes with feature-level explanations |
| 📊 **Confidence Intervals** | 95% CI from model disagreement analysis |
| 🌡️ **Smart Recommendations** | Actionable insights based on weather + farm conditions |
| 📈 **Model Comparison** | Side-by-side comparison of RF vs XGB vs LGBM |
| 📁 **Batch Processing** | Upload CSV, get predictions for thousands of farms |
| 🎚️ **What-If Simulator** | Adjust parameters and see yield impact in real-time |
| 📜 **Prediction History** | Full audit trail with SQLite persistence |
| 🐳 **Docker Ready** | One command deployment with `docker-compose up` |
| 🧪 **Tested** | Comprehensive test suite with pytest |
| 🔄 **CI/CD** | GitHub Actions pipeline for lint, test, build |
| 🎨 **Pro UI** | Dark-mode AgTech dashboard with Plotly charts |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **ML Models** | scikit-learn, XGBoost, LightGBM | Ensemble prediction |
| **Explainability** | SHAP | Feature importance & explanations |
| **Backend API** | FastAPI + Uvicorn | REST API serving |
| **Frontend** | Streamlit + Plotly | Interactive dashboard |
| **Validation** | Pydantic v2 | Input/output schemas |
| **Database** | SQLAlchemy + SQLite | Prediction history |
| **Logging** | structlog | Structured JSON logging |
| **Containerization** | Docker + Compose | Deployment |
| **CI/CD** | GitHub Actions | Automated testing |
| **Config** | pydantic-settings | Environment management |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Yashas14/Predictive_Analytics_for_Future_Ready_Farming.git
cd Predictive_Analytics_for_Future_Ready_Farming/smart-farm-ai

# Start everything
docker-compose up --build

# Access:
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Clone and navigate
git clone https://github.com/Yashas14/Predictive_Analytics_for_Future_Ready_Farming.git
cd Predictive_Analytics_for_Future_Ready_Farming/smart-farm-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Copy data files to data/ directory
mkdir -p data
cp ../farm_data-1646897931981.csv-20231125T090142Z-001/farm_data-1646897931981.csv data/
cp ../train_weather-1646897968670.csv-20231125T090155Z-001/train_weather-1646897968670.csv data/
# (copy train_data.csv as well)

# Train the model
python -m backend.ml.train --data-dir ./data

# Start backend (terminal 1)
uvicorn backend.api.main:app --reload --port 8000

# Start frontend (terminal 2)
streamlit run frontend/app.py
```

---

## 📡 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check + model status |
| `POST` | `/api/v1/predict` | Single yield prediction |
| `POST` | `/api/v1/predict/batch` | Batch prediction (CSV upload) |
| `GET` | `/api/v1/analytics/feature-importance` | Feature importance scores |
| `GET` | `/api/v1/analytics/model-metrics` | R², RMSE, MAE metrics |
| `GET` | `/api/v1/analytics/historical-predictions` | Prediction history |
| `GET` | `/api/v1/analytics/model-comparison` | Model comparison data |
| `POST` | `/api/v1/data/upload` | Upload new training data |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Example Response

```json
{
  "predicted_yield": 2450.75,
  "confidence_interval_lower": 2270.50,
  "confidence_interval_upper": 2631.00,
  "confidence_level": 0.95,
  "model_version": "1.0.0",
  "yield_category": "medium",
  "shap_values": {
    "farm_area": 0.234,
    "temp_obs": -0.112,
    "precipitation": 0.089
  },
  "recommendation": "✅ Temperature (25.3°C) is within optimal range..."
}
```

---

## 📂 Project Structure

```
smart-farm-ai/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # SQLAlchemy models
│   │   ├── middleware.py        # CORS + logging middleware
│   │   └── routes/
│   │       ├── predict.py       # POST /predict, /predict/batch
│   │       ├── analytics.py     # GET /analytics/*
│   │       ├── upload.py        # POST /data/upload
│   │       └── health.py        # GET /health
│   ├── ml/
│   │   ├── pipeline.py          # sklearn Pipeline builder
│   │   ├── train.py             # Training script
│   │   ├── evaluation.py        # Metrics & cross-validation
│   │   ├── explainability.py    # SHAP integration
│   │   └── models/
│   │       ├── random_forest.py
│   │       ├── xgboost_model.py
│   │       ├── lightgbm_model.py
│   │       └── ensemble.py      # VotingRegressor
│   ├── data/
│   │   ├── preprocessing.py     # Data cleaning (no hardcoded paths)
│   │   ├── validator.py         # Pydantic schemas
│   │   └── loader.py            # CSV loading utilities
│   └── utils/
│       ├── config.py            # pydantic-settings
│       └── logger.py            # structlog setup
├── frontend/
│   ├── app.py                   # Main Streamlit app
│   ├── styles.py                # CSS + theme utilities
│   ├── api_client.py            # Backend API client
│   └── pages/
│       ├── dashboard.py         # 🏠 KPIs + quick predict
│       ├── predictor.py         # 🔬 Full prediction form
│       ├── analytics.py         # 📊 Charts + metrics
│       ├── batch.py             # 📁 CSV batch processing
│       └── history.py           # 📈 Prediction history
├── models/                      # Versioned saved models
│   └── v1/
│       ├── model.pkl
│       └── metadata.json
├── data/                        # CSV data files
├── tests/
│   ├── test_api.py
│   └── test_ml.py
├── .github/workflows/ci.yml     # GitHub Actions CI
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=backend --cov-report=term-missing

# Run specific test file
pytest tests/test_ml.py -v

# Run specific test class
pytest tests/test_api.py::TestPredictEndpoint -v
```

---

## 🔧 Configuration

Configuration is managed via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `models/v1/model.pkl` | Path to trained model |
| `DATABASE_URL` | `sqlite:///./predictions.db` | Database connection string |
| `API_PORT` | `8000` | Backend API port |
| `BACKEND_URL` | `http://localhost:8000` | Backend URL for frontend |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MODEL_VERSION` | `1.0.0` | Current model version |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest tests/ -v`
5. Commit: `git commit -m 'feat: add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance

---

## 📸 Screenshots

> *Screenshots will be added after the first deployment*

| Dashboard | Predictor | Analytics |
|-----------|-----------|-----------|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Predictor](docs/screenshots/predictor.png) | ![Analytics](docs/screenshots/analytics.png) |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with 🌾 by [Yashas](https://github.com/Yashas14)**

*Transforming agriculture with intelligent data-driven decisions*

</div>
