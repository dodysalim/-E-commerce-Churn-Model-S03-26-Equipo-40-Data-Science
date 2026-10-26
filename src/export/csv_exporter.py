"""
src.export.csv_exporter — Exportación CSV Local con Vistas Resumidas
====================================================================
Responsabilidad única: exportar los resultados del modelo a archivos
CSV estructurados para revisión offline y respaldo.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Exporta los resultados del pipeline a archivos CSV organizados.

    Genera los siguientes archivos en exports_dir:
    - customer_churn_results.csv      : Tabla completa para Power BI
    - risk_segments_summary.csv       : Resumen ejecutivo por segmento
    - vip_at_risk.csv                 : Clientes VIP en zona de riesgo
    - top_priority_customers.csv      : Top 50 clientes a contactar primero

    Parámetros
    ----------
    exports_dir : str | Path
        Directorio de salida. Por defecto 'data/exports'.
    """

    def __init__(self, exports_dir: str | Path = "data/exports") -> None:
        self.exports_dir = Path(exports_dir)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def export_full_results(self, df: pd.DataFrame) -> Path:
        """Exporta el DataFrame completo con todas las columnas."""
        path = self.exports_dir / "customer_churn_results.csv"
        df.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"Resultados completos exportados: {path} ({len(df):,} clientes)")
        return path

    def export_risk_summary(self, df: pd.DataFrame) -> Path:
        """
        Exporta un resumen ejecutivo por segmento de riesgo.

        Columnas: RiskSegment, total_customers, avg_churn_probability,
                  total_monetary_exposure, pct_of_total.
        """
        if "RiskSegment" not in df.columns:
            raise ValueError("Se requiere la columna 'RiskSegment'.")

        agg_cols = {"ChurnProbability": ["count", "mean"]}
        if "Monetary" in df.columns:
            agg_cols["Monetary"] = "sum"

        summary = df.groupby("RiskSegment").agg(agg_cols).round(4)
        summary.columns = ["total_customers", "avg_churn_probability"] + (
            ["total_monetary_exposure"] if "Monetary" in df.columns else []
        )
        summary["pct_of_total"] = (summary["total_customers"] / summary["total_customers"].sum() * 100).round(2)
        summary = summary.reset_index()

        path = self.exports_dir / "risk_segments_summary.csv"
        summary.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"Resumen de segmentos exportado: {path}")
        return path

    def export_vip_at_risk(self, df: pd.DataFrame) -> Path:
        """Exporta los clientes VIP en zona de riesgo (acción crítica)."""
        if "CustomerLevel" not in df.columns or "RiskSegment" not in df.columns:
            raise ValueError("Se requieren columnas 'CustomerLevel' y 'RiskSegment'.")

        vip_at_risk = df[
            (df["CustomerLevel"] == "VIP / Champion")
            & (df["RiskSegment"].isin(["Riesgo Muy Alto", "Riesgo Medio"]))
        ].sort_values("ChurnProbability", ascending=False) if "ChurnProbability" in df.columns else df

        path = self.exports_dir / "vip_at_risk.csv"
        vip_at_risk.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"VIP en riesgo exportados: {path} ({len(vip_at_risk):,} clientes)")
        return path

    def export_top_priority_customers(self, df: pd.DataFrame, n: int = 50) -> Path:
        """Exporta el top N de clientes con mayor prioridad de contacto."""
        df_copy = df.copy()
        if "Monetary" in df_copy.columns and "ChurnProbability" in df_copy.columns:
            df_copy["PriorityScore"] = df_copy["Monetary"] * df_copy["ChurnProbability"]
            top = df_copy.nlargest(n, "PriorityScore")
        else:
            top = df_copy.head(n)

        path = self.exports_dir / "top_priority_customers.csv"
        top.to_csv(path, index=False, encoding="utf-8")
        logger.info(f"Top {n} clientes prioritarios exportados: {path}")
        return path

    def export_all(self, df: pd.DataFrame) -> dict[str, Path]:
        """
        Ejecuta todas las exportaciones en una sola llamada.

        Retorna
        -------
        dict
            Mapa de nombre → ruta de cada archivo exportado.
        """
        logger.info("Iniciando exportación completa de resultados CSV...")
        exported = {}

        exported["full_results"] = self.export_full_results(df)

        try:
            exported["risk_summary"] = self.export_risk_summary(df)
        except Exception as e:
            logger.warning(f"No se pudo exportar risk_summary: {e}")

        try:
            exported["vip_at_risk"] = self.export_vip_at_risk(df)
        except Exception as e:
            logger.warning(f"No se pudo exportar vip_at_risk: {e}")

        try:
            exported["top_priority"] = self.export_top_priority_customers(df)
        except Exception as e:
            logger.warning(f"No se pudo exportar top_priority_customers: {e}")

        logger.info(f"✅ Exportación CSV completada: {len(exported)} archivos en '{self.exports_dir}'")
        return exported
