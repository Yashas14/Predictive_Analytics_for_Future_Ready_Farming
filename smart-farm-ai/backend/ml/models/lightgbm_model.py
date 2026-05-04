"""LightGBM config."""

from lightgbm import LGBMRegressor


def get_lightgbm(
    n_estimators: int = 200,
    learning_rate: float = 0.05,
    max_depth: int = -1,
    num_leaves: int = 31,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    random_state: int = 42
) -> LGBMRegressor:
    """Tuned LightGBM regressor."""
    return LGBMRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        num_leaves=num_leaves,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=random_state,
        n_jobs=-1,
        verbose=-1
    )
