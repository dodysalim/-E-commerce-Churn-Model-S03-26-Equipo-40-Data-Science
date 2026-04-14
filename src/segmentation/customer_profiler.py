"""
src.segmentation.customer_profiler — Perfilado Estadístico por Segmento
========================================================================
Responsabilidad única: generar perfiles estadísticos descriptivos
para cada segmento de clientes, listos para incluir en reportes.
"""
from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class CustomerProfiler:
    """
    Genera estadísticas descriptivas por segmento de riesgo y nivel de cliente.

    Útil para entender qué caracteriza a cada grupo y formular
    estrategias de retención diferenciadas.
    """

    SEGMENT_COL = "RiskSegment"
    LEVEL_COL = "CustomerLevel"
    NUMERIC_COLS = ["Recency", "Frequency", "Monetary", "ChurnProbability"]

    def profile_by_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estadísticas por segmento de riesgo (Muy Alto, Medio, Estable).

        Retorna
        -------
        pd.DataFrame
            Tabla pivotada con medias, medianas y desviaciones por segmento.
        """
        if self.SEGMENT_COL not in df.columns:
            raise ValueError(f"Se requiere la columna '{self.SEGMENT_COL}'.")

        available_cols = [c for c in self.NUMERIC_COLS if c in df.columns]
        profile = (
            df.groupby(self.SEGMENT_COL)[available_cols]
            .agg(["mean", "median", "std", "count"])
            .round(2)
        )
        logger.info(f"Perfel por segmento de riesgo generado para {len(df):,} clientes.")
        return profile

    def profile_by_level(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estadísticas por nivel de cliente RFM (VIP, Leales, En Riesgo).

        Retorna
        -------
        pd.DataFrame
            Tabla de perfiles por CustomerLevel.
        """
        if self.LEVEL_COL not in df.columns:
            raise ValueError(f"Se requiere la columna '{self.LEVEL_COL}'.")

        available_cols = [c for c in self.NUMERIC_COLS if c in df.columns]
        profile = (
            df.groupby(self.LEVEL_COL)[available_cols]
            .agg(["mean", "median", "std", "count"])
            .round(2)
        )
        logger.info("Perfil por nivel de cliente RFM generado.")
        return profile

    def exposure_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula la exposición monetaria por segmento de riesgo.

        Crucial para priorizar esfuerzos de retención por impacto financiero.

        Retorna
        -------
        pd.DataFrame
            Tabla con: segmento, clientes_en_riesgo, exposure_total, exposure_media.
        """
        if "Monetary" not in df.columns or self.SEGMENT_COL not in df.columns:
            raise ValueError("Se requieren columnas 'Monetary' y 'RiskSegment'.")

        summary = (
            df.groupby(self.SEGMENT_COL)
            .agg(
                clientes=("Monetary", "count"),
                exposure_total=("Monetary", "sum"),
                exposure_media=("Monetary", "mean"),
                churn_prob_media=("ChurnProbability", "mean") if "ChurnProbability" in df.columns else ("Monetary", "count"),
            )
            .round(2)
            .sort_values("exposure_total", ascending=False)
            .reset_index()
        )
        logger.info("Resumen de exposición monetaria por segmento generado.")
        return summary

    def top_at_risk_customers(self, df: pd.DataFrame, n: int = 50) -> pd.DataFrame:
        """
        Retorna los N clientes más valiosos con mayor riesgo de fuga.

        Priorización: mayor Monetary × mayor ChurnProbability.

        Parámetros
        ----------
        n : int
            Número de clientes a retornar. Por defecto 50.

        Retorna
        -------
        pd.DataFrame
            Lista priorizada de clientes para acciones de retención inmediata.
        """
        df = df.copy()
        if "Monetary" in df.columns and "ChurnProbability" in df.columns:
            df["PriorityScore"] = df["Monetary"] * df["ChurnProbability"]
            top = df.nlargest(n, "PriorityScore")
        else:
            top = df.nlargest(n, "ChurnProbability") if "ChurnProbability" in df.columns else df.head(n)

        logger.info(f"Top {n} clientes prioritarios para retención identificados.")
        return top

    def generate_narrative_report(self, df: pd.DataFrame) -> str:
        """
        Genera un resumen narrativo del estado de la base de clientes.

        Retorna
        -------
        str
            Texto en Markdown con hallazgos principales.
        """
        total = len(df)
        lines = ["## 📋 Resumen del Perfilado de Clientes", ""]

        if "RiskSegment" in df.columns:
            dist = df["RiskSegment"].value_counts(normalize=True) * 100
            high_risk_pct = dist.get("Riesgo Muy Alto", 0)
            lines += [
                f"- **{total:,} clientes** analizados en total.",
                f"- **{high_risk_pct:.1f}%** se encuentran en **Riesgo Muy Alto** de abandono.",
            ]

        if "CustomerLevel" in df.columns and "RiskSegment" in df.columns:
            vip_at_risk = len(df[
                (df["CustomerLevel"] == "VIP / Champion")
                & (df["RiskSegment"].isin(["Riesgo Muy Alto", "Riesgo Medio"]))
            ])
            lines.append(f"- **{vip_at_risk:,}** clientes VIP están en zona de riesgo — **acción prioritaria**.")

        if "Monetary" in df.columns and "RiskSegment" in df.columns:
            exposure = df[df["RiskSegment"] == "Riesgo Muy Alto"]["Monetary"].sum()
            lines.append(f"- **Exposición monetaria** en Riesgo Muy Alto: **£{exposure:,.2f}**.")

        return "\n".join(lines)
