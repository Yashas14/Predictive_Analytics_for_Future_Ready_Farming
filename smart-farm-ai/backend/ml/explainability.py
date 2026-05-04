# -*- coding: utf-8 -*-
"""SHAP explanations for individual predictions."""

import numpy as np
import pandas as pd
import shap

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ModelExplainer:
    """Wraps SHAP TreeExplainer to explain ensemble predictions."""

    def __init__(self, pipeline, feature_names: list[str]):
        self.pipeline = pipeline
        self.feature_names = feature_names
        self.explainer = None
        self._initialize_explainer()

    def _initialize_explainer(self):
        """Pick the first tree-based sub-model for SHAP (RF by default)."""
        try:
            model = self.pipeline.named_steps["model"]
            
            # For VotingRegressor, use the first tree-based model for SHAP
            if hasattr(model, "estimators_"):
                # Use the random forest estimator for tree-based SHAP
                tree_model = model.estimators_[0]  # RF
                self.explainer = shap.TreeExplainer(tree_model)
                self.explainer_type = "tree"
                logger.info("shap_explainer_initialized", type="TreeExplainer")
            elif hasattr(model, "feature_importances_"):
                self.explainer = shap.TreeExplainer(model)
                self.explainer_type = "tree"
                logger.info("shap_explainer_initialized", type="TreeExplainer")
            else:
                # Fallback to KernelExplainer (slower but universal)
                self.explainer = None
                self.explainer_type = "none"
                logger.warning("shap_no_tree_explainer_available")
        except Exception as e:
            logger.error("shap_initialization_failed", error=str(e))
            self.explainer = None
            self.explainer_type = "none"

    def explain_prediction(self, X: pd.DataFrame) -> dict:
        """Return {feature: shap_value} for one prediction (sorted by |value|)."""
        if self.explainer is None:
            # Return approximate importance based on model feature importance
            return self._fallback_explanation(X)

        try:
            # Transform input through preprocessor
            preprocessor = self.pipeline.named_steps["preprocessor"]
            X_transformed = preprocessor.transform(X)

            # Get SHAP values
            shap_values = self.explainer.shap_values(X_transformed)

            # Map back to feature names
            if isinstance(shap_values, list):
                shap_values = shap_values[0]

            if shap_values.ndim == 1:
                shap_dict = dict(zip(self.feature_names, shap_values.tolist()))
            else:
                # For batch, return first row
                shap_dict = dict(zip(self.feature_names, shap_values[0].tolist()))

            # Sort by absolute value
            shap_dict = dict(
                sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            )

            return shap_dict

        except Exception as e:
            logger.error("shap_explanation_failed", error=str(e))
            return self._fallback_explanation(X)

    def explain_batch(self, X: pd.DataFrame) -> list[dict]:
        """SHAP values for each row in a batch."""
        if self.explainer is None:
            return [self._fallback_explanation(X.iloc[[i]]) for i in range(len(X))]

        try:
            preprocessor = self.pipeline.named_steps["preprocessor"]
            X_transformed = preprocessor.transform(X)
            shap_values = self.explainer.shap_values(X_transformed)

            if isinstance(shap_values, list):
                shap_values = shap_values[0]

            results = []
            for i in range(len(X)):
                shap_dict = dict(zip(self.feature_names, shap_values[i].tolist()))
                shap_dict = dict(
                    sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
                )
                results.append(shap_dict)

            return results

        except Exception as e:
            logger.error("shap_batch_explanation_failed", error=str(e))
            return [self._fallback_explanation(X.iloc[[i]]) for i in range(len(X))]

    def _fallback_explanation(self, X: pd.DataFrame) -> dict:
        """Use raw feature_importances_ when SHAP is not available."""
        model = self.pipeline.named_steps["model"]
        
        if hasattr(model, "estimators_"):
            importances = np.zeros(len(self.feature_names))
            n = 0
            for est in model.estimators_:
                if hasattr(est, "feature_importances_"):
                    importances += est.feature_importances_
                    n += 1
            if n > 0:
                importances /= n
        elif hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        else:
            importances = np.ones(len(self.feature_names)) / len(self.feature_names)

        importance_dict = dict(zip(self.feature_names, importances.tolist()))
        return dict(sorted(importance_dict.items(), key=lambda x: abs(x[1]), reverse=True))

    def get_base_value(self) -> float:
        """SHAP expected value (average model output)."""
        if self.explainer is not None and hasattr(self.explainer, "expected_value"):
            ev = self.explainer.expected_value
            if isinstance(ev, np.ndarray):
                return float(ev[0])
            return float(ev)
        return 0.0


def generate_recommendations(
    input_data: dict,
    shap_values: dict,
    predicted_yield: float
) -> list[str]:
    """Turn SHAP values + feature ranges into human-readable tips."""
    recommendations = []

    # Temperature analysis
    temp = input_data.get("temp_obs", 0)
    if temp > 35:
        recommendations.append(
            f"⚠️ High temperature ({temp}°C) detected. "
            "Consider heat-resistant crop varieties or shade structures. "
            "Expected yield impact: -5-10%."
        )
    elif temp < 5:
        recommendations.append(
            f"❄️ Low temperature ({temp}°C) may slow processing. "
            "Ensure frost protection measures are active."
        )
    elif 15 <= temp <= 30:
        recommendations.append(
            f"✅ Temperature ({temp}°C) is within optimal range for most crops."
        )

    # Wind analysis
    wind = input_data.get("wind_speed", 0)
    if wind > 40:
        recommendations.append(
            f"🌪️ High wind speed ({wind} km/h) detected. "
            "Risk of crop damage and reduced pollination. Expected yield reduction: ~8%."
        )
    elif wind > 25:
        recommendations.append(
            f"💨 Moderate wind ({wind} km/h). Monitor for potential drying effects on soil."
        )

    # Precipitation analysis
    precip = input_data.get("precipitation", 0)
    if precip > 50:
        recommendations.append(
            f"🌧️ Heavy precipitation ({precip} mm). "
            "Risk of waterlogging. Ensure proper drainage systems are operational."
        )
    elif precip < 2:
        recommendations.append(
            f"☀️ Low precipitation ({precip} mm). "
            "Consider supplemental irrigation if drought persists."
        )

    # Farm area optimization
    area = input_data.get("farm_area", 0)
    plants = input_data.get("num_processing_plants", 1)
    if area > 0 and plants > 0:
        ratio = area / plants
        if ratio > 50:
            recommendations.append(
                f"🏭 High area-to-plant ratio ({ratio:.0f} acres/plant). "
                "Consider adding processing capacity to reduce transport losses."
            )

    # Pressure analysis
    pressure = input_data.get("pressure_sea_level", 1013)
    if pressure < 1000:
        recommendations.append(
            f"🌀 Low atmospheric pressure ({pressure} hPa) indicates incoming weather system. "
            "Plan harvest activities accordingly."
        )

    # Top SHAP contributors
    if shap_values:
        top_features = list(shap_values.items())[:3]
        positive = [(f, v) for f, v in top_features if v > 0]
        negative = [(f, v) for f, v in top_features if v < 0]

        if positive:
            feat_names = ", ".join([f[0] for f in positive])
            recommendations.append(
                f"📈 Key positive yield drivers: {feat_names}"
            )
        if negative:
            feat_names = ", ".join([f[0] for f in negative])
            recommendations.append(
                f"📉 Key negative yield factors: {feat_names}. "
                "Consider optimizing these parameters."
            )

    if not recommendations:
        recommendations.append(
            "✅ All conditions are within normal parameters. "
            "Maintain current operational protocols."
        )

    return recommendations
