"""
src.segmentation.rfm_segmenter — Segmentación RFM Clásica
==========================================================
Responsabilidad única: calcular puntajes RFM (cuartiles 1-4)
y asignar el nivel de cliente (VIP, Leal, En Riesgo).
"""
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class RFMSegmenter:
    """
    Aplica la metodología de segmentación RFM clásica por cuartiles.

    Puntajes:
    - R_Score : Recency  — menor es mejor (4 = más reciente)
    - F_Score : Frequency — mayor es mejor (4 = más frecuente)
    - M_Score : Monetary — mayor es mejor (4 = mayor gasto)
    - RFM_Score : Suma de R+F+M (3-12)

    Niveles de cliente:
    - 'VIP / Champion'      : RFM_Score >= 9
    - 'Leales / Prometedores': RFM_Score >= 6
    - 'En Riesgo / Perdidos' : RFM_Score < 6

    Parámetros
    ----------
    vip_threshold : int
        Puntaje RFM mínimo para ser VIP. Por defecto 9.
    loyal_threshold : int
        Puntaje RFM mínimo para Leales. Por defecto 6.
    """

    def __init__(self, vip_threshold: int = 9, loyal_threshold: int = 6) -> None:
        self.vip_threshold = vip_threshold
        self.loyal_threshold = loyal_threshold

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula los scores RFM y asigna el nivel de cliente.

        Parámetros
        ----------
        df : pd.DataFrame
            DataFrame con columnas 'Recency', 'Frequency', 'Monetary'.

        Retorna
        -------
        pd.DataFrame
            DataFrame con columnas añadidas: R_Score, F_Score, M_Score,
            RFM_Group, RFM_Score, CustomerLevel.
        """
        required = {"Recency", "Frequency", "Monetary"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Columnas faltantes para RFM scoring: {missing}")

        df = df.copy()

        # Recency: menor valor = mejor = score 4
        df["R_Score"] = pd.qcut(df["Recency"], q=4, labels=[4, 3, 2, 1], duplicates="drop")

        # Frequency: mayor valor = mejor = score 4
        df["F_Score"] = pd.qcut(
            df["Frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4], duplicates="drop"
        )

        # Monetary: mayor valor = mejor = score 4
        df["M_Score"] = pd.qcut(df["Monetary"], q=4, labels=[1, 2, 3, 4], duplicates="drop")

        # Convertir a int para poder sumar
        df["R_Score"] = df["R_Score"].astype(int)
        df["F_Score"] = df["F_Score"].astype(int)
        df["M_Score"] = df["M_Score"].astype(int)

        # Código RFM y score total
        df["RFM_Group"] = (
            df["R_Score"].astype(str) + df["F_Score"].astype(str) + df["M_Score"].astype(str)
        )
        df["RFM_Score"] = df["R_Score"] + df["F_Score"] + df["M_Score"]

        # Nivel de cliente
        df["CustomerLevel"] = df["RFM_Score"].apply(self._assign_level)

        # Log de distribución
        dist = df["CustomerLevel"].value_counts()
        logger.info("Distribución de niveles de cliente (RFM):")
        for level, count in dist.items():
            logger.info(f"  {level:<30} : {count:>6,} ({count/len(df)*100:.1f}%)")

        return df

    def _assign_level(self, score: int) -> str:
        """Asigna el nivel del cliente según su RFM Score."""
        if score >= self.vip_threshold:
            return "VIP / Champion"
        elif score >= self.loyal_threshold:
            return "Leales / Prometedores"
        else:
            return "En Riesgo / Perdidos"
