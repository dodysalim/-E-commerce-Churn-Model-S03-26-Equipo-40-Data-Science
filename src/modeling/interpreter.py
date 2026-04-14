"""
src.modeling.interpreter — Interpretabilidad con SHAP
=====================================================
Responsabilidad única: generar y exportar explicaciones SHAP
del modelo seleccionado para auditoría y comunicación de resultados.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Estilo consistente
plt.style.use("seaborn-v0_8-whitegrid")


class ModelInterpreter:
    """
    Genera interpretabilidad SHAP para modelos de churn.

    Soporta:
    - TreeExplainer para Random Forest y XGBoost
    - LinearExplainer para Logistic Regression

    Parámetros
    ----------
    figures_dir : str | Path
        Directorio donde exportar los gráficos SHAP. Por defecto 'reports/figures/shap'.
    sample_size : int
        Número de muestras para calcular SHAP (performance). Por defecto 500.
    max_display : int
        Número máximo de features en el summary plot. Por defecto 15.
    """

    def __init__(
        self,
        figures_dir: str | Path = "reports/figures/shap",
        sample_size: int = 500,
        max_display: int = 15,
    ) -> None:
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.sample_size = sample_size
        self.max_display = max_display
        self._explainer: Optional[Any] = None
        self._shap_values: Optional[np.ndarray] = None
        self._X_sample: Optional[pd.DataFrame] = None

    def explain(self, model: Any, model_name: str, X_train: pd.DataFrame) -> "ModelInterpreter":
        """
        Calcula valores SHAP para el modelo dado.

        Parámetros
        ----------
        model : Any
            Modelo entrenado (RF, XGBoost o LogisticRegression).
        model_name : str
            Nombre del modelo para seleccionar el explainer correcto.
        X_train : pd.DataFrame
            Datos de entrenamiento para calcular valores SHAP.

        Retorna
        -------
        ModelInterpreter
            La instancia con los valores SHAP calculados.
        """
        try:
            import shap
        except ImportError:
            raise ImportError("SHAP no está instalado. Ejecuta: pip install shap")

        # Muestra para rendimiento
        n_sample = min(self.sample_size, len(X_train))
        self._X_sample = X_train.sample(n=n_sample, random_state=42)
        logger.info(f"Calculando SHAP para {model_name} con {n_sample} muestras...")

        if model_name in ("RandomForest", "XGBoost"):
            self._explainer = shap.TreeExplainer(model)
            shap_values_raw = self._explainer.shap_values(self._X_sample)
            # Para RF, shap_values es una lista [clase_0, clase_1] — usamos clase_1 (churn)
            if isinstance(shap_values_raw, list):
                self._shap_values = shap_values_raw[1]
            else:
                self._shap_values = shap_values_raw
        else:
            self._explainer = shap.LinearExplainer(model, self._X_sample)
            self._shap_values = self._explainer.shap_values(self._X_sample)

        logger.info(f"SHAP values calculados: shape={self._shap_values.shape}")
        return self

    def plot_summary(self) -> Path:
        """Genera el SHAP Summary Plot (beeswarm) y lo exporta."""
        import shap
        self._check_fitted()

        fig, ax = plt.subplots(figsize=(10, 6))
        shap.summary_plot(
            self._shap_values,
            self._X_sample,
            max_display=self.max_display,
            show=False,
        )
        plt.title("SHAP Summary Plot — Importancia de Features para Churn", fontsize=13, fontweight="bold")
        output_path = self.figures_dir / "shap_summary_plot.png"
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"SHAP Summary Plot guardado en: {output_path}")
        return output_path

    def plot_bar_importance(self) -> Path:
        """Genera el SHAP Feature Importance bar chart."""
        import shap
        self._check_fitted()

        shap.summary_plot(
            self._shap_values,
            self._X_sample,
            plot_type="bar",
            max_display=self.max_display,
            show=False,
        )
        plt.title("Importancia de Features (SHAP Mean |value|)", fontsize=13, fontweight="bold")
        output_path = self.figures_dir / "shap_feature_importance_bar.png"
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"SHAP Bar chart guardado en: {output_path}")
        return output_path

    def plot_dependence(self, feature: str, interaction_feature: Optional[str] = None) -> Path:
        """Genera un SHAP Dependence Plot para una feature específica."""
        import shap
        self._check_fitted()

        if feature not in self._X_sample.columns:
            raise ValueError(f"Feature '{feature}' no está en los datos.")

        shap.dependence_plot(
            feature,
            self._shap_values,
            self._X_sample,
            interaction_index=interaction_feature,
            show=False,
        )
        plt.title(f"SHAP Dependence Plot — {feature}", fontsize=13, fontweight="bold")
        safe_name = feature.replace(" ", "_").lower()
        output_path = self.figures_dir / f"shap_dependence_{safe_name}.png"
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"SHAP Dependence Plot guardado en: {output_path}")
        return output_path

    def get_feature_importance_df(self) -> pd.DataFrame:
        """
        Retorna un DataFrame ordenado por importancia SHAP media absoluta.

        Retorna
        -------
        pd.DataFrame
            Columnas: feature, mean_abs_shap
        """
        self._check_fitted()
        importance = np.abs(self._shap_values).mean(axis=0)
        df = pd.DataFrame({
            "feature": self._X_sample.columns.tolist(),
            "mean_abs_shap": importance,
        }).sort_values("mean_abs_shap", ascending=False)
        return df.reset_index(drop=True)

    def _check_fitted(self) -> None:
        """Verifica que explain() fue llamado antes de graficar."""
        if self._shap_values is None or self._X_sample is None:
            raise RuntimeError("Ejecuta explain() antes de generar gráficos.")
