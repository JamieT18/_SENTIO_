"""
Explainable AI utilities for Sentio (SHAP, LIME)
"""
import numpy as np
import shap
import lime
import lime.lime_tabular
from typing import Any, Dict
from sentio.core.logger import SentioLogger

structured_logger = SentioLogger.get_structured_logger("explainable_ai")

class ExplainableAI:
    def __init__(self, model, feature_names=None, regime: str = None, external_context: dict = None, ensemble: list = None):
        self.model = model
        self.feature_names = feature_names
        self.regime = regime
        self.external_context = external_context
        self.ensemble = ensemble or []

    def shap_explain(self, X: np.ndarray, regime: str = None, external_context: dict = None) -> Dict[str, Any]:
        structured_logger.log_event(
            "shap_explain",
            "Running SHAP explanation",
            {"input_shape": X.shape, "regime": regime or self.regime, "external_context": external_context or self.external_context}
        )
        try:
            result = self._shap_explain_logic(X, regime=regime, external_context=external_context)
            structured_logger.log_event(
                "shap_explain_result",
                "SHAP explanation completed",
                {"result_summary": str(result)[:200], "regime": regime or self.regime, "external_context": external_context or self.external_context}
            )
            return result
        except Exception as e:
            structured_logger.log_event(
                "shap_explain_error",
                str(e),
                {"input_shape": X.shape, "regime": regime or self.regime, "external_context": external_context or self.external_context, "exception": repr(e)},
                level="error"
            )
            raise

    def lime_explain(self, X: np.ndarray, instance_idx: int = 0, regime: str = None, external_context: dict = None) -> Dict[str, Any]:
        structured_logger.log_event(
            "lime_explain",
            "Running LIME explanation",
            {"input_shape": X.shape, "instance_idx": instance_idx, "regime": regime or self.regime, "external_context": external_context or self.external_context}
        )
        try:
            result = self._lime_explain_logic(X, instance_idx, regime=regime, external_context=external_context)
            structured_logger.log_event(
                "lime_explain_result",
                "LIME explanation completed",
                {"result_summary": str(result)[:200], "regime": regime or self.regime, "external_context": external_context or self.external_context}
            )
            return result
        except Exception as e:
            structured_logger.log_event(
                "lime_explain_error",
                str(e),
                {"input_shape": X.shape, "instance_idx": instance_idx, "regime": regime or self.regime, "external_context": external_context or self.external_context, "exception": repr(e)},
                level="error"
            )
            raise

    def _shap_explain_logic(self, X: np.ndarray, regime: str = None, external_context: dict = None) -> Dict[str, Any]:
        # Support ensemble explanations
        if self.ensemble:
            ensemble_explanations = []
            for model in self.ensemble:
                explainer = shap.Explainer(model, X)
                shap_values = explainer(X)
                ensemble_explanations.append({
                    'values': shap_values.values.tolist(),
                    'base_values': shap_values.base_values.tolist(),
                    'feature_names': self.feature_names or [f'Feature_{i}' for i in range(X.shape[1])],
                    'regime': regime,
                    'external_context': external_context
                })
            return {'ensemble_explanations': ensemble_explanations}
        else:
            explainer = shap.Explainer(self.model, X)
            shap_values = explainer(X)
            summary = {
                'values': shap_values.values.tolist(),
                'base_values': shap_values.base_values.tolist(),
                'feature_names': self.feature_names or [f'Feature_{i}' for i in range(X.shape[1])],
                'regime': regime,
                'external_context': external_context
            }
            return summary

    def _lime_explain_logic(self, X: np.ndarray, instance_idx: int, regime: str = None, external_context: dict = None) -> Dict[str, Any]:
        explainer = lime.lime_tabular.LimeTabularExplainer(
            X,
            feature_names=self.feature_names or [f'Feature_{i}' for i in range(X.shape[1])],
            verbose=False,
            mode='regression'
        )
        exp = explainer.explain_instance(X[instance_idx], self.model.predict)
        explanation = {
            'instance': X[instance_idx].tolist(),
            'explanation': exp.as_list(),
            'regime': regime,
            'external_context': external_context
        }
        return explanation
