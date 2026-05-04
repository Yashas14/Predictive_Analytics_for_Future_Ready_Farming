"""Evaluation helpers: metrics, cross-val, model comparison."""

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_validate
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    make_scorer
)

from backend.utils.logger import get_logger
from backend.utils.config import settings

logger = get_logger(__name__)


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """R², RMSE, MAE, MSE in one shot."""
    metrics = {
        "r2_score": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mean_squared_error(y_true, y_pred)),
    }
    
    logger.info("model_evaluated", **metrics)
    return metrics


def cross_validate_model(
    pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    cv: int = None
) -> dict:
    """K-fold cross-validation; returns mean ± std for R², RMSE, MAE."""
    cv = cv or settings.cv_folds
    
    scoring = {
        "r2": "r2",
        "neg_rmse": make_scorer(
            lambda y_true, y_pred: -np.sqrt(mean_squared_error(y_true, y_pred))
        ),
        "neg_mae": "neg_mean_absolute_error",
    }
    
    logger.info("starting_cross_validation", cv_folds=cv)
    
    cv_results = cross_validate(
        pipeline, X, y,
        cv=cv,
        scoring=scoring,
        return_train_score=True,
        n_jobs=-1
    )
    
    metrics = {
        "cv_r2_mean": float(np.mean(cv_results["test_r2"])),
        "cv_r2_std": float(np.std(cv_results["test_r2"])),
        "cv_rmse_mean": float(-np.mean(cv_results["test_neg_rmse"])),
        "cv_rmse_std": float(np.std(cv_results["test_neg_rmse"])),
        "cv_mae_mean": float(-np.mean(cv_results["test_neg_mae"])),
        "cv_mae_std": float(np.std(cv_results["test_neg_mae"])),
        "cv_train_r2_mean": float(np.mean(cv_results["train_r2"])),
    }
    
    logger.info("cross_validation_complete", **metrics)
    return metrics


def compare_models(
    models: dict,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series
) -> pd.DataFrame:
    """Train each model separately and return a comparison table."""
    from backend.ml.pipeline import build_preprocessor
    
    results = []
    
    for name, model in models.items():
        logger.info("training_model", model_name=name)
        
        from sklearn.pipeline import Pipeline
        pipe = Pipeline([
            ("preprocessor", build_preprocessor()),
            ("model", model)
        ])
        
        pipe.fit(X_train, y_train)
        
        train_pred = pipe.predict(X_train)
        test_pred = pipe.predict(X_test)
        
        train_metrics = evaluate_model(y_train.values, train_pred)
        test_metrics = evaluate_model(y_test.values, test_pred)
        
        results.append({
            "model": name,
            "train_r2": train_metrics["r2_score"],
            "test_r2": test_metrics["r2_score"],
            "train_rmse": train_metrics["rmse"],
            "test_rmse": test_metrics["rmse"],
            "train_mae": train_metrics["mae"],
            "test_mae": test_metrics["mae"],
        })
    
    comparison_df = pd.DataFrame(results)
    logger.info("model_comparison_complete", n_models=len(results))
    return comparison_df


def get_feature_importance(pipeline, feature_names: list[str]) -> dict:
    """Average feature importances across ensemble sub-models."""
    model = pipeline.named_steps["model"]
    
    # For VotingRegressor, average feature importances from tree-based models
    importances = np.zeros(len(feature_names))
    n_models = 0
    
    if hasattr(model, "estimators_"):
        # VotingRegressor after fitting
        for estimator in model.estimators_:
            if hasattr(estimator, "feature_importances_"):
                importances += estimator.feature_importances_
                n_models += 1
    elif hasattr(model, "feature_importances_"):
        # Single model
        importances = model.feature_importances_
        n_models = 1
    
    if n_models > 0:
        importances = importances / n_models
    
    importance_dict = dict(zip(feature_names, importances.tolist()))
    # Sort by importance (descending)
    importance_dict = dict(
        sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
    )
    
    return importance_dict
