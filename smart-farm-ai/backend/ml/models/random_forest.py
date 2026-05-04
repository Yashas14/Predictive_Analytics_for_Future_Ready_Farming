"""Random Forest config."""

from sklearn.ensemble import RandomForestRegressor


def get_random_forest(
    n_estimators: int = 200,
    max_depth: int = 20,
    min_samples_leaf: int = 2,
    min_samples_split: int = 2,
    random_state: int = 42
) -> RandomForestRegressor:
    """Tuned RF regressor."""
    return RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        min_samples_split=min_samples_split,
        max_features="sqrt",
        n_jobs=-1,
        random_state=random_state,
        verbose=0
    )
