"""
src.segmentation.risk_segmenter — Segmentación por Riesgo de Churn
==================================================================
Responsabilidad única: asignar probabilidad de churn y categorizar
a los clientes en segmentos de riesgo accionables.
"""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class RiskSegmenter:
    """
    Asigna probabilidades de churn y segmenta clientes por nivel de riesgo.

    Segmentos generados:
    - 'Riesgo Muy Alto' : ChurnProbability >= high_threshold
    - 'Riesgo Medio'    : ChurnProbability >= medium_threshold
    - 'Estable'         : ChurnProbability < medium_threshold

    Parámetros
    ----------
    high_threshold : float
        Umbral de probabilidad para riesgo muy alto. Por defecto 0.70.
    medium_threshold : float
        Umbral de probabilidad para riesgo medio. Por defecto 0.40.
    features : list[str]
        Lista de features que el modelo espera al predecir.
    """

    SEGMENT_ORDER = ["Riesgo Muy Alto", "Riesgo Medio", "Estable (Riesgo Bajo)"]

    def __init__(
        self,
        features: list[str],
        high_threshold: float = 0.70,
        medium_threshold: float = 0.40,
    ) -> None:
        self.features = features
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def transform(self, df: pd.DataFrame, model: Any) -> pd.DataFrame:
        """
        Predice probabilidades de churn y asigna segmentos de riesgo.

        Parámetros
        ----------
        df : pd.DataFrame
            DataFrame con las features del modelo.
        model : Any
            Modelo entrenado con método predict_proba().

        Retorna
        -------
        pd.DataFrame
            DataFrame con columnas 'ChurnProbability' y 'RiskSegment' añadidas.
        """
        missing = [f for f in self.features if f not in df.columns]
        if missing:
            raise ValueError(f"Features faltantes para predicción: {missing}")

        df = df.copy()
        df["ChurnProbability"] = model.predict_proba(df[self.features])[:, 1]
        df["RiskSegment"] = df["ChurnProbability"].apply(self._categorize)

        # Log de distribución
        dist = df["RiskSegment"].value_counts()
        total = len(df)
        logger.info("Distribución de segmentos de riesgo:")
        for segment in self.SEGMENT_ORDER:
            count = dist.get(segment, 0)
            pct = count / total * 100
            logger.info(f"  {segment:<30} : {count:>6,} ({pct:.1f}%)")

        return df

    def _categorize(self, prob: float) -> str:
        """Categoriza una probabilidad en su segmento de riesgo."""
        if prob >= self.high_threshold:
            return "Riesgo Muy Alto"
        elif prob >= self.medium_threshold:
            return "Riesgo Medio"
        else:
            return "Estable (Riesgo Bajo)"

    def get_high_risk_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra y retorna solo los clientes de riesgo muy alto."""
        if "RiskSegment" not in df.columns:
            raise RuntimeError("Ejecuta transform() primero.")
        return df[df["RiskSegment"] == "Riesgo Muy Alto"].copy()

    def get_vip_at_risk(self, df: pd.DataFrame, vip_level: str = "VIP / Champion") -> pd.DataFrame:
        """Retorna clientes VIP en zona de riesgo medio-alto."""
        if "CustomerLevel" not in df.columns:
            raise RuntimeError("Se requiere la columna 'CustomerLevel' (ejecuta RFMSegmenter primero).")
        return df[
            (df["CustomerLevel"] == vip_level)
            & (df["RiskSegment"].isin(["Riesgo Muy Alto", "Riesgo Medio"]))
        ].sort_values("ChurnProbability", ascending=False).copy()
