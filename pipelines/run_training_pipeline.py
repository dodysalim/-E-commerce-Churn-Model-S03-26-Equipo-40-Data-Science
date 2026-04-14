"""
pipelines/run_training_pipeline.py — Pipeline de Entrenamiento Aislado
======================================================================
Ejecuta únicamente el flujo de entrenamiento:
  - Carga datos procesados (rfm_with_churn.parquet)
  - Escala features
  - Entrena y evalúa modelos
  - Registra el modelo champion

Requiere que run_full_pipeline.py haya sido ejecutado al menos una vez
para generar los datos procesados.
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

logger = logging.getLogger("pipelines.training")

from src.features.scaler import FeatureScaler
from src.modeling.trainer import ModelTrainer
from src.modeling.evaluator import ModelEvaluator
from src.modeling.interpreter import ModelInterpreter
from src.modeling.registry import ModelRegistry


def run():
    logger.info("🤖 Training Pipeline — Iniciando...")

    with open(PROJECT_ROOT / "config" / "config.yaml") as f:
        cfg = yaml.safe_load(f)

    model_cfg = cfg["modeling"]
    data_path = Path(cfg["paths"]["processed_rfm_churn"])

    if not data_path.exists():
        logger.error(f"❌ Datos procesados no encontrados: {data_path}")
        logger.error("   Ejecuta primero: python pipelines/run_full_pipeline.py")
        sys.exit(1)

    df = pd.read_parquet(data_path)
    logger.info(f"Datos cargados: {len(df):,} clientes")

    # Features
    base_features = ["Recency", "Frequency", "Monetary"]
    advanced_features = [
        f for f in ["AvgTicket", "DaysBetweenPurchases", "MonetaryStdDev", "UniqueProducts", "PeakHourBuyer"]
        if f in df.columns
    ]
    features = base_features + advanced_features

    # Escalar
    scaler = FeatureScaler(features=features)
    df_scaled = scaler.fit_transform(df)

    # Entrenar
    trainer = ModelTrainer(
        features=features,
        target="CHURN",
        test_size=model_cfg["test_size"],
        cv_folds=model_cfg["cv_folds"],
        random_state=model_cfg["random_state"],
        primary_metric=model_cfg["primary_metric"],
    )
    trainer.fit(df_scaled)

    # Evaluar
    evaluator = ModelEvaluator()
    test_metrics = evaluator.evaluate(
        trainer.best_model, trainer.best_model_name, trainer.X_test, trainer.y_test
    )
    evaluator.plot_roc_curve({trainer.best_model_name: trainer.best_model}, trainer.X_test, trainer.y_test)
    evaluator.plot_confusion_matrix(trainer.best_model, trainer.X_test, trainer.y_test, trainer.best_model_name)

    # Actualizar metrics.md
    metrics_md = evaluator.generate_metrics_markdown(trainer.cv_results, test_metrics)
    Path("reports/metrics.md").write_text(metrics_md, encoding="utf-8")

    # Registrar
    scaler.save("models/champion/scaler.pkl")
    registry = ModelRegistry()
    registry.save(
        model=trainer.best_model,
        model_name=trainer.best_model_name,
        features=features,
        metrics=test_metrics,
        make_champion=True,
    )

    # SHAP
    interpreter = ModelInterpreter()
    try:
        interpreter.explain(trainer.best_model, trainer.best_model_name, trainer.X_train)
        interpreter.plot_summary()
        interpreter.plot_bar_importance()
    except Exception as e:
        logger.warning(f"SHAP omitido: {e}")

    logger.info(f"✅ Training Pipeline completado. Champion: {trainer.best_model_name} | Recall: {test_metrics['recall']:.4f}")


if __name__ == "__main__":
    run()
