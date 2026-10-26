"""
pipelines/run_export_pipeline.py — Pipeline de Exportación Aislado
==================================================================
Carga los resultados finales ya generados y los exporta a:
  - Supabase (si las credenciales están configuradas)
  - CSV locales en data/exports/

No re-entrena el modelo. Solo exporta los resultados existentes.
"""
from __future__ import annotations

import logging
import logging.config
import os
import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

Path("logs").mkdir(exist_ok=True)
with open(PROJECT_ROOT / "config" / "logging_config.yaml") as f:
    logging.config.dictConfig(yaml.safe_load(f))

logger = logging.getLogger("pipelines.export")

from src.export.supabase_connector import SupabaseConnector
from src.export.csv_exporter import CSVExporter


def run():
    logger.info("☁️  Export Pipeline — Iniciando...")

    with open(PROJECT_ROOT / "config" / "config.yaml") as f:
        cfg = yaml.safe_load(f)

    results_path = Path(cfg["paths"]["processed_final"])

    if not results_path.exists():
        logger.error(f"❌ Resultados finales no encontrados: {results_path}")
        logger.error("   Ejecuta primero: python pipelines/run_full_pipeline.py")
        sys.exit(1)

    df = pd.read_parquet(results_path)
    logger.info(f"Resultados cargados: {len(df):,} clientes")

    # CSV Export
    logger.info("📄 Exportando a CSV...")
    csv_exporter = CSVExporter(exports_dir="data/exports")
    exported = csv_exporter.export_all(df)
    for name, path in exported.items():
        logger.info(f"  ✅ {name}: {path}")

    # Supabase Export
    logger.info("☁️  Exporting a Supabase...")
    supabase = SupabaseConnector(env_file=PROJECT_ROOT.parent / ".env")
    try:
        if supabase.test_connection():
            supabase.sync_churn_results(df)
            logger.info("✅ Supabase actualizado correctamente.")
        else:
            logger.warning("⚠️  Supabase no disponible. Solo se exportó a CSV.")
    except Exception as e:
        logger.warning(f"⚠️  Supabase omitido: {e}")

    logger.info("✅ Export Pipeline completado.")


if __name__ == "__main__":
    run()
