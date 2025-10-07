"""
Advanced Explainability for Sentio
Integrate SHAP and LIME for trade decisions
"""
import shap
import lime
import numpy as np

class ExplainabilityEngine:
    def __init__(self, model):
        self.model = model

    def explain_shap(self, X):
        explainer = shap.Explainer(self.model, X)
        shap_values = explainer(X)
        return shap_values

    def explain_lime(self, X):
        explainer = lime.lime_tabular.LimeTabularExplainer(X)
        explanation = explainer.explain_instance(X[0], self.model.predict)
        return explanation
