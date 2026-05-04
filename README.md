<div align="center">

# 🌾 Predictive Analytics for Future-Ready Farming

**A production-grade agricultural yield intelligence platform powered by Ensemble ML, SHAP Explainability, and a FastAPI + interactive web dashboard.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-blue)](https://xgboost.readthedocs.io)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.3+-green)](https://lightgbm.readthedocs.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](smart-farm-ai/LICENSE)

[Overview](#-overview) · [Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Project Structure](#-project-structure) · [Results](#-model-results) · [Connect](#-connect)

</div>

---

## 📌 Overview

Agricultural yield prediction is critical for food security, supply chain planning, and farm economics. Traditional approaches rely on simplistic models or manual estimation, leading to inaccurate forecasts with no explainability.

This repository contains **two complementary solutions**:

| Component | Description |
|-----------|-------------|
| 📓 **Notebook / Scripts** (root) | End-to-end exploratory analysis, data preprocessing, baseline ML model training and evaluation |
| 🚀 **AgriSense AI** (`smart-farm-ai/`) | Production-grade REST API + interactive web dashboard with ensemble ML, SHAP explainability, confidence intervals, and prediction history |

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Ensemble ML** | VotingRegressor combining RandomForest + XGBoost + LightGBM |
| 🔍 **SHAP Explainability** | Every prediction comes with per-feature impact scores |
| 📊 **Confidence Intervals** | 95% CI derived from model disagreement analysis |
| 🌡️ **Smart Recommendations** | Actionable insights based on weather + farm conditions |
| 📈 **Model Comparison** | Side-by-side metrics: RF vs XGB vs LGBM |
| 📁 **Batch Processing** | Upload a CSV, get predictions for thousands of farm records |
| 🎚️ **What-If Simulator** | Adjust parameters and see yield impact in real-time |
| 📜 **Prediction History** | Full audit trail persisted in SQLite via SQLAlchemy |
| 🐳 **Docker Ready** | One-command deployment with `docker-compose up --build` |
| 🧪 **Tested** | Comprehensive pytest suite (API + ML layers) |
| 🔄 **CI/CD** | GitHub Actions pipeline for lint, test, and build |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        AGRISENSE AI                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐   HTTP/JSON   ┌──────────────────────┐ │
│  │  WEB FRONTEND   │ ◄───────────► │   FASTAPI BACKEND    │ │
│  │  (HTML/CSS/JS)  │               │                      │ │
│  │  • Dashboard    │               │  • POST /predict     │ │
│  │  • Predictor    │               │  • POST /predict/    │ │
│  │  • Analytics    │               │         batch        │ │
│  │  • Batch Upload │               │  • GET  /analytics/* │ │
│  │  • History      │               │  • POST /data/upload │ │
│  └─────────────────┘               │  • GET  /health      │ │
│                                    └──────────┬───────────┘ │
│                                               │             │
│                                   ┌───────────▼──────────┐  │
│                                   │      ML ENGINE       │  │
│                                   │  Preprocessor        │  │
│                                   │  → Ensemble          │  │
│                                   │    (RF+XGB+LGB)      │  │
│                                   │  → SHAP Explainer    │  │
│                                   └───────────┬──────────┘  │
│                                               │             │
│                                   ┌───────────▼──────────┐  │
│                                   │   SQLite Database    │  │
│                                   │  (Prediction History)│  │
│                                   └──────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **ML Models** | scikit-learn, XGBoost, LightGBM | Ensemble yield prediction |
| **Explainability** | SHAP | Feature importance per prediction |
| **Backend API** | FastAPI + Uvicorn | High-performance REST API |
| **Frontend** | HTML5 + CSS3 + Vanilla JS | Interactive AgTech dashboard |
| **Validation** | Pydantic v2 | Input/output schema enforcement |
| **Database** | SQLAlchemy + SQLite | Prediction audit trail |
| **Logging** | structlog | Structured JSON logging |
| **Containerization** | Docker + Compose | Reproducible deployment |
| **CI/CD** | GitHub Actions | Automated lint → test → build |
| **Config** | pydantic-settings | Env-based configuration |

---

## 🚀 Quick Start

### Option 1 — Docker (Recommended)

```bash
git clone https://github.com/Yashas14/Predictive_Analytics_for_Future_Ready_Farming.git
cd Predictive_Analytics_for_Future_Ready_Farming/smart-farm-ai

docker-compose up --build
```

| Service | URL |
|---------|-----|
| Web Dashboard | http://localhost:8000 |
| REST API | http://localhost:8000/api/v1 |
| Interactive API Docs | http://localhost:8000/docs |

---

### Option 2 — Local Development

```bash
# 1. Clone repository
git clone https://github.com/Yashas14/Predictive_Analytics_for_Future_Ready_Farming.git
cd Predictive_Analytics_for_Future_Ready_Farming

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Install dependencies
cd smart-farm-ai
pip install -r requirements.txt

# 4. Set up environment config
cp .env.example .env

# 5. Ensure data files are in place
#    smart-farm-ai/data/ should contain:
#    - farm_data.csv
#    - train_data.csv
#    - train_weather.csv

# 6. Train the model
python -m backend.ml.train --data-dir ./data

# 7. Start the backend + frontend
uvicorn backend.api.main:app --reload --port 8000
```

The frontend is served statically by FastAPI at **http://localhost:8000**.

---

### Option 3 — Notebook / Baseline Script

```bash
pip install pandas matplotlib scikit-learn

# Run baseline training
python setup_and_train.py

# Or explore interactively
jupyter notebook Solution_Robust_Yield_Prediction_for_Farm_Processing_Units-checkpoint.ipynb
```

---

## 📡 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check + model status |
| `POST` | `/api/v1/predict` | Single farm yield prediction |
| `POST` | `/api/v1/predict/batch` | Batch predictions via CSV upload |
| `GET` | `/api/v1/analytics/feature-importance` | Feature importance scores |
| `GET` | `/api/v1/analytics/model-metrics` | R², RMSE, MAE metrics |
| `GET` | `/api/v1/analytics/historical-predictions` | Prediction history |
| `GET` | `/api/v1/analytics/model-comparison` | RF vs XGB vs LGBM comparison |
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
Predictive_Analytics_for_Future_Ready_Farming/
│
├── 📓 Notebook & Baseline Scripts
│   ├── Solution_Robust_Yield_Prediction_...-checkpoint.ipynb
│   ├── final_yield_prediction.py
│   ├── setup_and_train.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📊 Raw Data Files
│   ├── farm_data-...csv/
│   ├── train_weather-...csv/
│   └── test_weather-...csv/
│
└── 🚀 smart-farm-ai/             ← Production Application
    ├── backend/
    │   ├── api/
    │   │   ├── main.py           # FastAPI app entrypoint
    │   │   ├── database.py       # SQLAlchemy models
    │   │   ├── middleware.py     # CORS + logging
    │   │   └── routes/
    │   │       ├── predict.py    # /predict, /predict/batch
    │   │       ├── analytics.py  # /analytics/*
    │   │       ├── upload.py     # /data/upload
    │   │       └── health.py     # /health
    │   ├── ml/
    │   │   ├── pipeline.py       # sklearn Pipeline builder
    │   │   ├── train.py          # Training script
    │   │   ├── evaluation.py     # Metrics & cross-validation
    │   │   ├── explainability.py # SHAP integration
    │   │   └── models/
    │   │       ├── ensemble.py   # VotingRegressor
    │   │       ├── random_forest.py
    │   │       ├── xgboost_model.py
    │   │       └── lightgbm_model.py
    │   ├── data/
    │   │   ├── loader.py         # CSV loading utilities
    │   │   ├── preprocessing.py  # Feature engineering
    │   │   └── validator.py      # Pydantic schemas
    │   └── utils/
    │       ├── config.py         # pydantic-settings
    │       └── logger.py         # structlog setup
    ├── frontend/
    │   ├── index.html            # Main SPA entry point
    │   ├── css/
    │   │   ├── styles.css
    │   │   ├── components.css
    │   │   └── pages.css
    │   └── js/
    │       ├── app.js
    │       ├── api.js
    │       ├── components.js
    │       └── pages/
    │           ├── dashboard.js
    │           ├── predictor.js
    │           ├── analytics.js
    │           ├── batch.js
    │           └── history.js
    ├── models/v1/                # Saved trained model + metadata
    ├── data/                     # Training data (CSV)
    ├── tests/
    │   ├── test_api.py
    │   └── test_ml.py
    ├── .github/workflows/ci.yml  # GitHub Actions CI/CD
    ├── docker-compose.yml
    ├── Dockerfile.backend
    ├── pyproject.toml
    └── requirements.txt
```

---

## 📊 Model Results

Trained on 3,070 records (2,456 train / 614 test) across 12 features:

| Model | Train R² | Test R² | Test RMSE | Test MAE |
|-------|----------|---------|-----------|----------|
| **Ensemble (RF+XGB+LGB)** | 0.977 | **0.894** | 736.4 | 344.7 |
| XGBoost | 0.989 | 0.894 | 736.6 | 339.9 |
| LightGBM | 0.967 | 0.894 | 737.5 | 356.9 |
| RandomForest | 0.964 | 0.879 | 787.1 | 399.0 |

**Cross-validation (5-fold):** R² = 0.900 ± 0.024

**Top 5 Features by Importance:**
1. `farm_area` — 515.8
2. `unix_sec` (time) — 306.3
3. `pressure_sea_level` — 215.3
4. `dew_temp` — 171.7
5. `temp_obs` — 162.7


<img width="1904" height="902" alt="Screenshot 2026-05-04 174824" src="https://github.com/user-attachments/assets/16c2bb85-e19e-4e26-8660-c16d2839f5be" />

--

<img width="1892" height="897" alt="image" src="https://github.com/user-attachments/assets/4ed4c676-b338-4b99-8255-f219432d89f1" />

--

<img width="1899" height="892" alt="image" src="https://github.com/user-attachments/assets/3009a76c-b02a-44e9-bae1-a014483ef6ad" />

--
<img width="1889" height="902" alt="image" src="https://github.com/user-attachments/assets/edfee2c9-057e-4ece-bd87-99f7e0d6f7ad" />

--

---

## 🔧 Configuration

Environment variables (see `smart-farm-ai/.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `models/v1/model.pkl` | Path to trained model |
| `DATABASE_URL` | `sqlite:///./predictions.db` | Database connection |
| `API_PORT` | `8000` | Backend port |
| `BACKEND_URL` | `http://localhost:8000` | Backend URL |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MODEL_VERSION` | `1.0.0` | Model version tag |

---

## 🧪 Running Tests

```bash
cd smart-farm-ai

# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=backend --cov-report=term-missing

# Specific test file
pytest tests/test_ml.py -v
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Add your changes and tests
4. Run the test suite: `pytest tests/ -v`
5. Commit using conventional commits: `git commit -m 'feat: add your feature'`
6. Push and open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see [smart-farm-ai/LICENSE](smart-farm-ai/LICENSE) for details.

---

<div align="center">

**Built with 🌾 by [Yashas D](https://github.com/Yashas14)**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yashasd2004/)

*Transforming agriculture with intelligent, data-driven decisions*

</div>
