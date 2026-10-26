"""
src.labeling.threshold_analyzer — Análisis del Umbral Óptimo de Churn
======================================================================
Responsabilidad única: analizar estadísticamente distintos umbrales
de inactividad para fundamentar la elección del threshold de churn.
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ThresholdAnalyzer:
    """
    Evalúa el impacto de distintos umbrales de inactividad sobre la
    distribución de clases churn/activo.

    Esto permite justificar el umbral elegido (ej. 90 días) con datos
    en lugar de hacerlo de forma arbitraria.

    Parámetros
    ----------
    thresholds : list[int]
        Lista de umbrales en días a evaluar.
        Por defecto: [30, 60, 90, 120, 150, 180].
    """

    def __init__(self, thresholds: Optional[list[int]] = None) -> None:
        self.thresholds = thresholds or [30, 60, 90, 120, 150, 180]
        self._results: Optional[pd.DataFrame] = None

    def analyze(self, rfm_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula la tasa de churn para cada umbral y devuelve un resumen.

        Parámetros
        ----------
        rfm_df : pd.DataFrame
            DataFrame RFM con columna 'Recency'.

        Retorna
        -------
        pd.DataFrame
            DataFrame con columnas: threshold_days, churn_count,
            active_count, churn_rate_pct, imbalance_ratio.
        """
        if "Recency" not in rfm_df.columns:
            raise ValueError("Se requiere la columna 'Recency'.")

        rows = []
        total = len(rfm_df)

        for threshold in self.thresholds:
            churned = (rfm_df["Recency"] > threshold).sum()
            active = total - churned
            rate = churned / total * 100
            ratio = active / churned if churned > 0 else np.inf

            rows.append({
                "threshold_days": threshold,
                "churn_count": int(churned),
                "active_count": int(active),
                "churn_rate_pct": round(rate, 2),
                "imbalance_ratio": round(ratio, 2),
            })

        results_df = pd.DataFrame(rows)
        self._results = results_df

        logger.info("Análisis de umbrales completado:")
        for _, row in results_df.iterrows():
            logger.info(
                f"  {row['threshold_days']}d → Churn: {row['churn_rate_pct']}% | "
                f"Ratio: 1:{row['imbalance_ratio']}"
            )

        return results_df

    def recommend_threshold(self, target_churn_rate: float = 0.25) -> int:
        """
        Recomienda el umbral más cercano a la tasa de churn objetivo.

        Parámetros
        ----------
        target_churn_rate : float
            Tasa de churn deseada (entre 0 y 1). Por defecto 0.25 (25%).

        Retorna
        -------
        int
            Umbral en días más cercano al target.
        """
        if self._results is None:
            raise RuntimeError("Ejecuta analyze() primero.")

        target_pct = target_churn_rate * 100
        closest_idx = (self._results["churn_rate_pct"] - target_pct).abs().idxmin()
        recommended = int(self._results.loc[closest_idx, "threshold_days"])
        actual_rate = self._results.loc[closest_idx, "churn_rate_pct"]

        logger.info(
            f"Umbral recomendado: {recommended} días "
            f"(tasa: {actual_rate}% vs objetivo: {target_pct}%)"
        )
        return recommended

    def get_recency_percentiles(self, rfm_df: pd.DataFrame) -> pd.Series:
        """Retorna los percentiles clave de Recency para orientar el análisis."""
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        return rfm_df["Recency"].describe(percentiles=[p / 100 for p in percentiles])

    @property
    def results(self) -> Optional[pd.DataFrame]:
        """Resultado del último análisis."""
        return self._results
