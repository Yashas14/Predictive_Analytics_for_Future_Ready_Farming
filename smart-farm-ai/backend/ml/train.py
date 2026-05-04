"""End-to-end training script for the ensemble pipeline."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from backend.data.loader import load_training_data
from backend.data.preprocessing import prepare_training_data, ALL_FEATURES
from backend.ml.pipeline import (
    build_pipeline,
    save_pipeline,
    ALL_PIPELINE_FEATURES
)
from backend.ml.evaluation import (
    evaluate_model,
    cross_validate_model,
    compare_models,
    get_feature_importance
)
from backend.ml.models.ensemble import get_individual_models
from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def train(
    data_dir: Path | None = None,
    save_dir: Path | None = None,
    test_size: float = 0.2,
    nrows: int | None = None
) -> dict:
    """Load data, fit pipeline, evaluate, save model. Returns metrics dict."""
    logger.info("training_started", data_dir=str(data_dir), test_size=test_size)
    
    # 1. Load data
    data_dir = data_dir or settings.abs_data_dir
    train_data, train_weather, farm_data = load_training_data(data_dir, nrows=nrows)
    
    # 2. Preprocess
    X, y = prepare_training_data(train_data, farm_data, train_weather)
    
    # Ensure we only use pipeline features
    available_features = [f for f in ALL_PIPELINE_FEATURES if f in X.columns]
    X = X[available_features]
    
    logger.info("data_prepared", X_shape=X.shape, y_shape=y.shape, features=available_features)
    
    # 3. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=settings.random_state
    )
    
    logger.info("data_split", train_size=len(X_train), test_size=len(X_test))
    
    # 4. Build and train the pipeline
    pipeline = build_pipeline(random_state=settings.random_state)
    pipeline.fit(X_train, y_train)
    
    # 5. Evaluate
    train_pred = pipeline.predict(X_train)
    test_pred = pipeline.predict(X_test)
    
    train_metrics = evaluate_model(y_train.values, train_pred)
    test_metrics = evaluate_model(y_test.values, test_pred)
    
    # 6. Cross-validation
    cv_metrics = cross_validate_model(pipeline, X, y)
    
    # 7. Model comparison (individual models)
    individual_models = get_individual_models(random_state=settings.random_state)
    comparison = compare_models(individual_models, X_train, X_test, y_train, y_test)
    
    # 8. Feature importance
    feature_importance = get_feature_importance(pipeline, available_features)
    
    # 9. Compile all metrics
    all_metrics = {
        "train": train_metrics,
        "test": test_metrics,
        "cross_validation": cv_metrics,
        "model_comparison": comparison.to_dict(orient="records"),
        "feature_importance": feature_importance,
        "n_train_samples": len(X_train),
        "n_test_samples": len(X_test),
        "n_features": len(available_features),
    }
    
    # 10. Save model
    model_path = save_pipeline(
        pipeline=pipeline,
        metrics=all_metrics,
        feature_names=available_features,
        save_dir=save_dir
    )
    
    logger.info(
        "training_complete",
        model_path=str(model_path),
        test_r2=test_metrics["r2_score"],
        test_rmse=test_metrics["rmse"]
    )
    
    return {
        "model_path": str(model_path),
        "metrics": all_metrics,
        "feature_names": available_features,
        "comparison": comparison,
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train the Smart Farm AI model")
    parser.add_argument(
        "--data-dir", type=Path, default=None,
        help="Path to data directory containing CSVs"
    )
    parser.add_argument(
        "--save-dir", type=Path, default=None,
        help="Path to save trained model"
    )
    parser.add_argument(
        "--nrows", type=int, default=None,
        help="Limit number of rows (for testing)"
    )
    parser.add_argument(
        "--test-size", type=float, default=0.2,
        help="Test split ratio"
    )
    
    args = parser.parse_args()
    
    results = train(
        data_dir=args.data_dir,
        save_dir=args.save_dir,
        test_size=args.test_size,
        nrows=args.nrows
    )
    
    print("\n" + "=" * 60)
    print("TRAINING RESULTS")
    print("=" * 60)
    print(f"Model saved to: {results['model_path']}")
    print(f"Test R²: {results['metrics']['test']['r2_score']:.4f}")
    print(f"Test RMSE: {results['metrics']['test']['rmse']:.4f}")
    print(f"Test MAE: {results['metrics']['test']['mae']:.4f}")
    print(f"CV R² (mean ± std): {results['metrics']['cross_validation']['cv_r2_mean']:.4f} ± {results['metrics']['cross_validation']['cv_r2_std']:.4f}")
    print("\nModel Comparison:")
    print(results["comparison"].to_string(index=False))
    print("\nTop 5 Features:")
    for i, (feat, imp) in enumerate(list(results["metrics"]["feature_importance"].items())[:5]):
        print(f"  {i+1}. {feat}: {imp:.4f}")
