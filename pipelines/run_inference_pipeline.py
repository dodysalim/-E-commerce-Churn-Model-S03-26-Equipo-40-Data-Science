"""
pipelines/run_inference_pipeline.py — Pipeline de Inferencia sobre Datos Nuevos
===============================================================================
Carga el modelo champion activo y genera predicciones de churn
para un nuevo dataset de transacciones.

Uso:
  python pipelines/run_inference_pipeline.py --input data/new_transactions.csv
"""
from __future__ import annotations

import argparse
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

logger = logging.getLogger("pipelines.inference")

from src.data.loader import DataLoader
from src.data.validator import DataValidator
from src.features.preprocessing import TransactionPreprocessor
from src.features.rfm_builder import RFMBuilder
from src.features.advanced_features import AdvancedFeatureEngineer
from src.features.scaler import FeatureScaler
from src.modeling.registry import ModelRegistry
from src.segmentation.risk_segmenter import RiskSegmenter
from src.segmentation.rfm_segmenter import RFMSegmenter
from src.export.csv_exporter import CSVExporter

import joblib


def run(input_path: str):
    logger.info(f"🔮 Inference Pipeline — Dataset: {input_path}")

    with open(PROJECT_ROOT / "config" / "config.yaml") as f:
        cfg = yaml.safe_load(f)

    # Cargar modelo champion
    registry = ModelRegistry()
    model, champion_info = registry.load_champion()
    features = champion_info.get("features", ["Recency", "Frequency", "Monetary"])
    logger.info(f"Champion cargado: {champion_info.get('model_name')} — Features: {features}")

    # Cargar scaler
    scaler_path = Path("models/champion/scaler.pkl")
    if scaler_path.exists():
        scaler = FeatureScaler.load(scaler_path, features=features)
    else:
        logger.warning("No se encontró scaler. Se aplicará sin escalamiento.")
        scaler = None

    # Cargar nuevos datos
    loader = DataLoader(input_path)
    raw_df = loader.load()

    validator = DataValidator(raise_on_error=False)
    validator.validate(raw_df)

    # Preprocesar
    preprocessor = TransactionPreprocessor()
    clean_df = preprocessor.fit_transform(raw_df)

    rfm_builder = RFMBuilder(apply_log_transform=True)
    rfm_df = rfm_builder.build(clean_df)

    adv_fe = AdvancedFeatureEngineer()
    rfm_enriched = adv_fe.build(clean_df, rfm_df)

    # Escalar
    if scaler:
        df_scaled = scaler.transform(rfm_enriched)
    else:
        df_scaled = rfm_enriched

    # Predecir
    churn_cfg = cfg["churn"]
    risk_segmenter = RiskSegmenter(
        features=features,
        high_threshold=churn_cfg["high_risk_threshold"],
        medium_threshold=churn_cfg["medium_risk_threshold"],
    )
    df_with_risk = risk_segmenter.transform(df_scaled, model)

    rfm_segmenter = RFMSegmenter()
    df_final = rfm_segmenter.transform(df_with_risk)

    # Exportar
    csv_exporter = CSVExporter(exports_dir="data/exports")
    csv_exporter.export_full_results(df_final)

    logger.info(f"✅ Inferencia completada: {len(df_final):,} clientes procesados.")
    high_risk = (df_final["RiskSegment"] == "Riesgo Muy Alto").sum()
    logger.info(f"   🔴 Clientes en Riesgo Muy Alto: {high_risk:,} ({high_risk/len(df_final)*100:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inferencia de Churn sobre nuevos datos.")
    cfg_default = "data/raw/online_retail_II.csv"
    parser.add_argument("--input", required=False, default=cfg_default,
                        help=f"Ruta al CSV de transacciones. Default: {cfg_default}")
    args = parser.parse_args()
    run(args.input)
