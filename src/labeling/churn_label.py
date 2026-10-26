"""
src.labeling.churn_label — Definición y Etiquetado de Churn
===========================================================
Responsabilidad única: aplicar el criterio de inactividad para
generar la variable objetivo CHURN en el DataFrame RFM.
"""
from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class ChurnLabeler:
    """
    Asigna la etiqueta de Churn (1) o Activo (0) según el criterio
    de inactividad basado en Recency.

    Definición de Churn:
      CHURN = 1 si Recency (días desde última compra) > threshold_days
      CHURN = 0 si el cliente compró dentro del período de análisis

    Parámetros
    ----------
    threshold_days : int
        Umbral de inactividad en días. Por defecto 90 días.
        Valor determinado analíticamente en notebooks/02_churn_definition.ipynb.
    """

    def __init__(self, threshold_days: int = 90) -> None:
        self.threshold_days = threshold_days
        self._report: Optional[dict] = None

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica la etiqueta de churn al DataFrame RFM.

        Parámetros
        ----------
        df : pd.DataFrame
            DataFrame RFM con columna 'Recency'.

        Retorna
        -------
        pd.DataFrame
            DataFrame con columna 'CHURN' añadida (0 o 1).

        Raises
        ------
        ValueError
            Si la columna 'Recency' no está presente.
        """
        if "Recency" not in df.columns:
            raise ValueError(
                "La columna 'Recency' es requerida para el etiquetado de Churn. "
                "Ejecuta RFMBuilder.build() antes de llamar a ChurnLabeler."
            )

        df = df.copy()
        df["CHURN"] = (df["Recency"] > self.threshold_days).astype(int)

        # Reporte de balance de clases
        total = len(df)
        churned = df["CHURN"].sum()
        active = total - churned
        churn_rate = churned / total * 100

        self._report = {
            "threshold_days": self.threshold_days,
            "total_customers": total,
            "churned": int(churned),
            "active": int(active),
            "churn_rate_pct": round(churn_rate, 2),
            "imbalance_ratio": round(active / churned, 2) if churned > 0 else None,
        }

        logger.info(
            f"Etiquetado completado (umbral: {self.threshold_days}d) | "
            f"Churn: {churned:,} ({churn_rate:.1f}%) | "
            f"Activos: {active:,} ({100 - churn_rate:.1f}%)"
        )

        if churn_rate < 10:
            logger.warning(
                f"⚠️ Tasa de Churn muy baja ({churn_rate:.1f}%). "
                f"Considera reducir el umbral o aplicar SMOTE en modelado."
            )
        elif churn_rate > 60:
            logger.warning(
                f"⚠️ Tasa de Churn muy alta ({churn_rate:.1f}%). "
                f"Verifica el umbral — podría estar demasiado bajo."
            )

        return df

    @property
    def report(self) -> Optional[dict]:
        """Retorna el reporte de balance de clases del último transform."""
        return self._report

    def print_report(self) -> None:
        """Imprime el reporte de distribución de etiquetas."""
        if self._report is None:
            print("No hay reporte disponible. Ejecuta transform() primero.")
            return
        print("\n=== Reporte de Etiquetado de Churn ===")
        print(f"  Umbral de inactividad : {self._report['threshold_days']} días")
        print(f"  Total de clientes     : {self._report['total_customers']:,}")
        print(f"  Churn (Inactivos)     : {self._report['churned']:,} ({self._report['churn_rate_pct']}%)")
        print(f"  Activos               : {self._report['active']:,} ({100 - self._report['churn_rate_pct']}%)")
        print(f"  Ratio de desbalance   : 1:{self._report['imbalance_ratio']} (Activo:Churn)")
