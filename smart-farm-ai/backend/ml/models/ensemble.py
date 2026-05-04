"""VotingRegressor combining RF, XGBoost, LightGBM."""

from sklearn.ensemble import VotingRegressor
from backend.ml.models.random_forest import get_random_forest
from backend.ml.models.xgboost_model import get_xgboost
from backend.ml.models.lightgbm_model import get_lightgbm


def get_ensemble(random_state: int = 42) -> VotingRegressor:
    """Build the 3-model voting ensemble."""
    rf = get_random_forest(random_state=random_state)
    xgb = get_xgboost(random_state=random_state)
    lgb = get_lightgbm(random_state=random_state)
    
    ensemble = VotingRegressor(
        estimators=[
            ("rf", rf),
            ("xgb", xgb),
            ("lgb", lgb)
        ],
        n_jobs=-1
    )
    
    return ensemble


def get_individual_models(random_state: int = 42) -> dict:
    """All three models as a dict (for comparison training)."""
    return {
        "random_forest": get_random_forest(random_state=random_state),
        "xgboost": get_xgboost(random_state=random_state),
        "lightgbm": get_lightgbm(random_state=random_state),
    }
