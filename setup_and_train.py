"""
Setup script: copies data, generates synthetic train_data, and trains the model.
Run from the project root (Predictive_Analytics_for_Future_Ready_Farming-main).
"""

import sys
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
SMART_FARM = ROOT / "smart-farm-ai"
DATA_OUT = SMART_FARM / "data"
DATA_OUT.mkdir(parents=True, exist_ok=True)

FARM_CSV_SRC  = ROOT / "farm_data-1646897931981.csv-20231125T090142Z-001" / "farm_data-1646897931981.csv"
WEATHER_CSV_SRC = ROOT / "train_weather-1646897968670.csv-20231125T090155Z-001" / "train_weather-1646897968670.csv"

# ── Step 1: Copy existing CSVs ─────────────────────────────────────────────
print("▶ Copying CSV data files to smart-farm-ai/data/ ...")
shutil.copy2(FARM_CSV_SRC,    DATA_OUT / "farm_data.csv")
shutil.copy2(WEATHER_CSV_SRC, DATA_OUT / "train_weather.csv")
print(f"  ✓ farm_data.csv  ({FARM_CSV_SRC.stat().st_size // 1024} KB)")
print(f"  ✓ train_weather.csv  ({WEATHER_CSV_SRC.stat().st_size // 1024} KB)")

# ── Step 2: Generate synthetic train_data.csv ──────────────────────────────
print("\n▶ Generating synthetic train_data.csv ...")

farm_df = pd.read_csv(DATA_OUT / "farm_data.csv")
weather_df = pd.read_csv(DATA_OUT / "train_weather.csv", nrows=5000)
weather_df["timestamp"] = pd.to_datetime(weather_df["timestamp"])

np.random.seed(42)

# Sample weather rows as the time dimension
weather_sample = weather_df.sample(n=min(3000, len(weather_df)), random_state=42).reset_index(drop=True)

# Sample farms (with replacement to get enough rows)
n_rows = len(weather_sample)
farm_sample = farm_df.sample(n=n_rows, replace=True, random_state=42).reset_index(drop=True)

ingredient_types = [
    "wheat", "corn", "soy", "barley", "oat",
    "sunflower", "canola", "rice", "sorghum", "millet"
]

# Build train_data (farming_company intentionally excluded — it comes from farm_data)
train_data = pd.DataFrame({
    "id": range(n_rows),
    "farm_id": farm_sample["farm_id"].values,
    "date": weather_sample["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").values,
    "yield": None,  # computed below
    "ingredient_type": np.random.choice(ingredient_types, n_rows),
})

# Simulate yield as a function of farm area + weather + noise
farm_area_vals = farm_sample["farm_area"].fillna(farm_sample["farm_area"].median()).values
temp_vals      = weather_sample["temp_obs"].fillna(25.0).values
wind_vals      = weather_sample["wind_speed"].fillna(10.0).values
precip_vals    = weather_sample["precipitation"].fillna(5.0).values
plants_vals    = farm_sample["num_processing_plants"].fillna(5.0).values

yield_base = (
    farm_area_vals * 2.5
    + np.clip(temp_vals, 10, 30) * 15
    - np.clip(wind_vals, 0, 50) * 3
    + np.clip(precip_vals, 0, 20) * 8
    + plants_vals * 50
)

# Add realistic noise (~20% std)
noise = np.random.normal(0, yield_base * 0.20)
train_data["yield"] = np.clip(yield_base + noise, 200, 8000).round(2)

out_path = DATA_OUT / "train_data.csv"
train_data.to_csv(out_path, index=False)
print(f"  ✓ train_data.csv  ({n_rows} rows, yield range: {train_data['yield'].min():.0f}–{train_data['yield'].max():.0f})")

# ── Step 3: Train the model ────────────────────────────────────────────────
print("\n▶ Training the ensemble ML pipeline ...")
sys.path.insert(0, str(SMART_FARM))

from backend.ml.train import train

results = train(
    data_dir=DATA_OUT,
    save_dir=SMART_FARM / "models" / "v1",
    nrows=2000  # use 2000 rows for a quick demo train
)

print("\n" + "=" * 60)
print("✅  TRAINING COMPLETE")
print("=" * 60)
m = results["metrics"]
print(f"  Test R²   : {m['test']['r2_score']:.4f}")
print(f"  Test RMSE : {m['test']['rmse']:.2f}")
print(f"  Test MAE  : {m['test']['mae']:.2f}")
print(f"  CV R²     : {m['cross_validation']['cv_r2_mean']:.4f} ± {m['cross_validation']['cv_r2_std']:.4f}")
print(f"\n  Model saved to : {results['model_path']}")
print("\nTop 5 feature importances:")
for feat, imp in list(m["feature_importance"].items())[:5]:
    bar = "█" * int(imp * 40)
    print(f"  {feat:<35} {bar}  {imp:.4f}")
