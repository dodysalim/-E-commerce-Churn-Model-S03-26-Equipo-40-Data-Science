"""
monitoring/drift_detector.py — Detección de Data Drift
=======================================================
Detecta si la distribución de los datos de entrada en producción
se ha desviado significativamente respecto al conjunto de entrenamiento.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Detecta data drift comparando distribuciones estadísticas.

    Métodos:
    - detect_with_evidently: usa Evidently AI para un reporte visual completo
    - detect_with_ks_test: Kolmogorov-Smirnov test (sin dependencias extra)

    Parámetros
    ----------
    reference_data_path : str | Path
        Ruta al dataset de referencia (entrenamiento). Por defecto Parquet de train.
    reports_dir : str | Path
        Directorio donde guardar los reportes de drift.
    """

    def __init__(
        self,
        reference_data_path: str | Path = "data/processed/train_test_splits/X_train.parquet",
        reports_dir: str | Path = "reports/drift",
    ) -> None:
        self.reference_data_path = Path(reference_data_path)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def detect_with_ks_test(
        self,
        current_df: pd.DataFrame,
        features: list[str],
        p_value_threshold: float = 0.05,
    ) -> dict[str, dict]:
        """
        Aplica el test de Kolmogorov-Smirnov por feature.

        Parámetros
        ----------
        current_df : pd.DataFrame
            Datos actuales de producción a comparar.
        features : list[str]
            Lista de features a evaluar.
        p_value_threshold : float
            Si p-value < threshold, se detecta drift. Por defecto 0.05.

        Retorna
        -------
        dict
            Por cada feature: {'statistic': float, 'p_value': float, 'drift_detected': bool}
        """
        from scipy.stats import ks_2samp

        if not self.reference_data_path.exists():
            raise FileNotFoundError(
                f"Datos de referencia no encontrados: {self.reference_data_path}\n"
                "Ejecuta el pipeline de entrenamiento primero."
            )

        reference_df = pd.read_parquet(self.reference_data_path)
        results = {}
        drift_count = 0

        logger.info("Ejecutando detección de drift (KS Test)...")
        for feature in features:
            if feature not in reference_df.columns or feature not in current_df.columns:
                logger.warning(f"Feature '{feature}' no encontrada en alguno de los datasets.")
                continue

            stat, p_value = ks_2samp(reference_df[feature].dropna(), current_df[feature].dropna())
            drift = p_value < p_value_threshold

            results[feature] = {
                "statistic": round(stat, 4),
                "p_value": round(p_value, 6),
                "drift_detected": drift,
            }

            if drift:
                drift_count += 1
                logger.warning(f"  ⚠️  DRIFT en '{feature}': KS={stat:.4f}, p={p_value:.6f}")
            else:
                logger.info(f"  ✅ Sin drift en '{feature}': KS={stat:.4f}, p={p_value:.6f}")

        logger.info(f"Drift detectado en {drift_count}/{len(results)} features.")
        return results

    def detect_with_evidently(
        self,
        current_df: pd.DataFrame,
        features: list[str],
        output_html: Optional[str] = None,
    ) -> dict:
        """
        Genera reporte de drift con Evidently AI (HTML interactivo).

        Parámetros
        ----------
        current_df : pd.DataFrame
            Datos actuales de producción.
        output_html : str, opcional
            Ruta del archivo HTML de salida. Por defecto 'reports/drift/drift_report.html'.

        Retorna
        -------
        dict
            Diccionario con métricas de drift de Evidently.
        """
        try:
            from evidently.metric_preset import DataDriftPreset
            from evidently.report import Report
        except ImportError:
            raise ImportError(
                "Evidently AI no está instalado. Ejecuta: pip install evidently>=0.4.30"
            )

        reference_df = pd.read_parquet(self.reference_data_path)
        available_features = [f for f in features if f in reference_df.columns and f in current_df.columns]

        report = Report(metrics=[DataDriftPreset()])
        report.run(
            reference_data=reference_df[available_features],
            current_data=current_df[available_features],
        )

        output_path = Path(output_html) if output_html else self.reports_dir / "drift_report.html"
        report.save_html(str(output_path))
        logger.info(f"Reporte de Evidently guardado en: {output_path}")

        # Extraer resumen
        result_dict = report.as_dict()
        drift_metrics = result_dict.get("metrics", [{}])[0].get("result", {})
        n_drifted = drift_metrics.get("number_of_drifted_columns", 0)
        logger.info(f"Evidently: {n_drifted} features con drift detectado.")
        return drift_metrics

    def save_drift_report_csv(self, drift_results: dict) -> Path:
        """Guarda el reporte de drift KS como CSV."""
        df = pd.DataFrame(drift_results).T.reset_index()
        df.columns = ["feature", "ks_statistic", "p_value", "drift_detected"]
        output_path = self.reports_dir / "ks_drift_report.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Reporte CSV de drift guardado en: {output_path}")
        return output_path
