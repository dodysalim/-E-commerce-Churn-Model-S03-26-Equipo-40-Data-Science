"""
pipelines/run_full_pipeline.py — Pipeline Completo End-to-End
=============================================================
Orquesta todos los pasos del pipeline de predicción de churn:
  1. Carga y validación del dataset
  2. Preprocesamiento y construcción RFM
  3. Features avanzadas
  4. Etiquetado de Churn
  5. Entrenamiento y evaluación de modelos
  6. Segmentación de clientes
  7. Exportación a Supabase y CSV
"""
from __future__ import annotations

import logging
import logging.config
import os
import sys
from pathlib import Path

import pandas as pd
import yaml

# ─── Path Resolution ─────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)  # Asegura que todas las rutas relativas sean desde la raíz

# ─── Configuración de Logging ─────────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
with open(PROJECT_ROOT / "config" / "logging_config.yaml") as f:
    logging.config.dictConfig(yaml.safe_load(f))

logger = logging.getLogger("pipelines.full")

# ─── Imports de Dominio ───────────────────────────────────────────────────────
from src.data.loader import DataLoader
from src.data.validator import DataValidator
from src.data.versioner import DataVersioner
from src.features.preprocessing import TransactionPreprocessor
from src.features.rfm_builder import RFMBuilder
from src.features.advanced_features import AdvancedFeatureEngineer
from src.features.scaler import FeatureScaler
from src.labeling.churn_label import ChurnLabeler
from src.modeling.trainer import ModelTrainer
from src.modeling.evaluator import ModelEvaluator
from src.modeling.interpreter import ModelInterpreter
from src.modeling.registry import ModelRegistry
from src.segmentation.risk_segmenter import RiskSegmenter
from src.segmentation.rfm_segmenter import RFMSegmenter
from src.segmentation.customer_profiler import CustomerProfiler
from src.export.supabase_connector import SupabaseConnector
from src.export.csv_exporter import CSVExporter


def load_config() -> dict:
    """Carga la configuración centralizada del proyecto."""
    config_path = PROJECT_ROOT / "config" / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def run():
    """Ejecuta el pipeline completo de churn prediction."""
    logger.info("=" * 65)
    logger.info("  🚀 E-Commerce Churn Prediction Pipeline — Iniciando...")
    logger.info("=" * 65)

    cfg = load_config()
    paths = cfg["paths"]
    churn_cfg = cfg["churn"]
    model_cfg = cfg["modeling"]
    export_cfg = cfg["export"]

    # ──────────────────────────────────────────────────────────────
    # PASO 1: Carga y validación del dataset
    # ──────────────────────────────────────────────────────────────
    logger.info("\n📥 [1/7] Carga y validación del dataset...")

    # Versioning del dataset para trazabilidad
    versioner = DataVersioner(paths["raw_data"])
    version_info = versioner.generate_version_info()
    versioner.save_version_info(version_info, "data/raw/dataset_version.json")

    loader = DataLoader(paths["raw_data"])
    raw_df = loader.load()

    validator = DataValidator(raise_on_error=True)
    val_report = validator.validate(raw_df)

    # ──────────────────────────────────────────────────────────────
    # PASO 2: Preprocesamiento y construcción RFM
    # ──────────────────────────────────────────────────────────────
    logger.info("\n🛠️  [2/7] Preprocesamiento y construcción de métricas RFM...")

    preprocessor = TransactionPreprocessor()
    clean_df = preprocessor.fit_transform(raw_df)

    # Guardar datos limpios (interim)
    Path("data/interim").mkdir(parents=True, exist_ok=True)
    clean_df.to_parquet("data/interim/cleaned_transactions.parquet", index=False)

    rfm_builder = RFMBuilder(apply_log_transform=True)
    rfm_df = rfm_builder.build(clean_df)

    # ──────────────────────────────────────────────────────────────
    # PASO 3: Features avanzadas
    # ──────────────────────────────────────────────────────────────
    logger.info("\n⚙️  [3/7] Generando features avanzadas de comportamiento...")

    feature_engineer = AdvancedFeatureEngineer()
    rfm_enriched = feature_engineer.build(clean_df, rfm_df)

    # ──────────────────────────────────────────────────────────────
    # PASO 4: Etiquetado de Churn
    # ──────────────────────────────────────────────────────────────
    logger.info(f"\n🏷️  [4/7] Etiquetando Churn (umbral: {churn_cfg['inactivity_threshold_days']} días)...")

    labeler = ChurnLabeler(threshold_days=churn_cfg["inactivity_threshold_days"])
    df_labeled = labeler.transform(rfm_enriched)
    labeler.print_report()

    # Guardar estado intermedio
    Path("data/interim").mkdir(parents=True, exist_ok=True)
    df_labeled.to_parquet("data/interim/rfm_raw.parquet", index=False)

    # ──────────────────────────────────────────────────────────────
    # PASO 5: Entrenamiento y evaluación de modelos
    # ──────────────────────────────────────────────────────────────
    logger.info("\n🤖 [5/7] Entrenando y evaluando modelos predictivos...")

    # Definir features para el modelo
    base_features = ["Recency", "Frequency", "Monetary"]
    advanced_features = [
        f for f in ["AvgTicket", "DaysBetweenPurchases", "MonetaryStdDev", "UniqueProducts", "PeakHourBuyer"]
        if f in df_labeled.columns
    ]
    features = base_features + advanced_features
    logger.info(f"Features de entrenamiento ({len(features)}): {features}")

    # Escalar features
    scaler = FeatureScaler(features=features)
    df_scaled = scaler.fit_transform(df_labeled)

    # Guardar train/test splits
    trainer = ModelTrainer(
        features=features,
        target="CHURN",
        test_size=model_cfg["test_size"],
        cv_folds=model_cfg["cv_folds"],
        random_state=model_cfg["random_state"],
        primary_metric=model_cfg["primary_metric"],
    )
    trainer.fit(df_scaled)

    # Guardar splits para reproducibilidad
    split_dir = Path("data/processed/train_test_splits")
    split_dir.mkdir(parents=True, exist_ok=True)
    trainer.X_train.to_parquet(split_dir / "X_train.parquet", index=False)
    trainer.X_test.to_parquet(split_dir / "X_test.parquet", index=False)
    trainer.y_train.to_frame().to_parquet(split_dir / "y_train.parquet", index=False)
    trainer.y_test.to_frame().to_parquet(split_dir / "y_test.parquet", index=False)

    # Evaluación en test set
    evaluator = ModelEvaluator()
    test_metrics = evaluator.evaluate(
        trainer.best_model, trainer.best_model_name, trainer.X_test, trainer.y_test
    )

    # Gráficos de evaluación
    all_models_fitted = {trainer.best_model_name: trainer.best_model}
    evaluator.plot_roc_curve(all_models_fitted, trainer.X_test, trainer.y_test)
    evaluator.plot_confusion_matrix(trainer.best_model, trainer.X_test, trainer.y_test, trainer.best_model_name)
    evaluator.plot_precision_recall_curve(trainer.best_model, trainer.X_test, trainer.y_test, trainer.best_model_name)

    # Actualizar metrics.md
    metrics_md = evaluator.generate_metrics_markdown(trainer.cv_results, test_metrics)
    Path("reports/metrics.md").write_text(metrics_md, encoding="utf-8")
    logger.info("reports/metrics.md actualizado con métricas reales.")

    # Registro del modelo
    registry = ModelRegistry()
    scaler_path = "models/champion/scaler.pkl"
    scaler.save(scaler_path)
    registry.save(
        model=trainer.best_model,
        model_name=trainer.best_model_name,
        features=features,
        metrics=test_metrics,
        make_champion=True,
    )

    # SHAP
    logger.info("\n🔍 Generando interpretabilidad SHAP...")
    interpreter = ModelInterpreter()
    try:
        interpreter.explain(trainer.best_model, trainer.best_model_name, trainer.X_train)
        interpreter.plot_summary()
        interpreter.plot_bar_importance()
        interpreter.plot_dependence("Recency")
    except Exception as e:
        logger.warning(f"SHAP no pudo completarse: {e}")

    # ──────────────────────────────────────────────────────────────
    # PASO 6: Segmentación de clientes
    # ──────────────────────────────────────────────────────────────
    logger.info("\n📊 [6/7] Segmentando clientes por riesgo y nivel RFM...")

    risk_segmenter = RiskSegmenter(
        features=features,
        high_threshold=churn_cfg["high_risk_threshold"],
        medium_threshold=churn_cfg["medium_risk_threshold"],
    )
    df_segmented = risk_segmenter.transform(df_scaled, trainer.best_model)

    rfm_segmenter = RFMSegmenter(
        vip_threshold=cfg["segmentation"]["vip_rfm_threshold"],
        loyal_threshold=cfg["segmentation"]["loyal_rfm_threshold"],
    )
    df_final = rfm_segmenter.transform(df_segmented)

    # Añadir Monetary original (sin escalar) para exportación
    if "Monetary" not in df_final.columns:
        df_final["Monetary"] = df_labeled["Monetary"].values

    # Perfilado narrativo
    profiler = CustomerProfiler()
    narrative = profiler.generate_narrative_report(df_final)
    logger.info(f"\n{narrative}")

    # Guardar resultado final
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df_final.to_parquet("data/processed/final_customer_results.parquet", index=False)
    df_labeled.to_parquet("data/processed/rfm_with_churn.parquet", index=False)

    # ──────────────────────────────────────────────────────────────
    # PASO 7: Exportación a Supabase y CSV
    # ──────────────────────────────────────────────────────────────
    logger.info("\n☁️  [7/7] Exportando resultados...")

    # Exportación CSV (siempre)
    csv_exporter = CSVExporter(exports_dir="data/exports")
    exported_files = csv_exporter.export_all(df_final)
    for name, path in exported_files.items():
        logger.info(f"  CSV: {path}")

    # Exportación a Supabase (solo si las credenciales están configuradas)
    supabase = SupabaseConnector(env_file=PROJECT_ROOT / ".env")
    try:
        if supabase.test_connection():
            supabase.sync_churn_results(df_final)
        else:
            logger.warning("⚠️  Supabase no disponible. Solo se exportó a CSV.")
    except Exception as e:
        logger.warning(f"⚠️  Exportación a Supabase omitida: {e}")

    # ──────────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 65)
    logger.info("  ✅ Pipeline completado exitosamente.")
    logger.info(f"  📁 Resultados en: data/exports/ y data/processed/")
    logger.info(f"  🏆 Modelo champion: {trainer.best_model_name}")
    logger.info(f"  🎯 Recall en test: {test_metrics['recall']:.4f}")
    logger.info("=" * 65 + "\n")


if __name__ == "__main__":
    run()
