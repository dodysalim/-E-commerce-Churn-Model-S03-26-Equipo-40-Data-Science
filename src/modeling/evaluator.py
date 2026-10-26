"""
src.modeling.evaluator — Evaluación Exhaustiva del Modelo
=========================================================
Responsabilidad única: evaluar el modelo seleccionado en el set
de test y generar reportes y gráficos de rendimiento.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    recall_score,
    roc_auc_score,
    roc_curve,
)

logger = logging.getLogger(__name__)

# Estilo consistente de gráficos
plt.style.use("seaborn-v0_8-whitegrid")
PALETTE = ["#2d6a4f", "#52b788", "#74c69d", "#d8f3dc"]


class ModelEvaluator:
    """
    Evalúa el modelo champion sobre el set de test.

    Genera:
    - Métricas tabulares (Recall, F1, AUC, Accuracy)
    - Curva ROC comparativa
    - Matriz de confusión
    - Curva Precision-Recall

    Parámetros
    ----------
    figures_dir : str | Path
        Directorio donde guardar los archivos PNG. Por defecto 'reports/figures/modeling'.
    """

    def __init__(self, figures_dir: str | Path = "reports/figures/modeling") -> None:
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self._metrics: Optional[dict] = None

    def evaluate(
        self,
        model: Any,
        model_name: str,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> dict:
        """
        Calcula métricas completas del modelo en el set de test.

        Retorna
        -------
        dict
            Diccionario con Recall, F1, AUC, Accuracy y reporte completo.
        """
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        acc = accuracy_score(y_test, y_pred)

        self._metrics = {
            "model_name": model_name,
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "auc": round(auc, 4),
            "accuracy": round(acc, 4),
        }

        logger.info(f"\n{'═'*50}")
        logger.info(f"  Métricas Finales — {model_name} (Test Set)")
        logger.info(f"{'═'*50}")
        logger.info(f"  Recall   : {recall:.4f}  ← Métrica prioritaria")
        logger.info(f"  F1 Score : {f1:.4f}")
        logger.info(f"  ROC-AUC  : {auc:.4f}")
        logger.info(f"  Accuracy : {acc:.4f}")
        logger.info(f"{'═'*50}")
        logger.info(f"\n{classification_report(y_test, y_pred, target_names=['Activo', 'Churn'])}")

        return self._metrics

    def plot_roc_curve(self, models_dict: dict, X_test: pd.DataFrame, y_test: pd.Series) -> Path:
        """
        Genera curva ROC comparativa para todos los modelos.

        Parámetros
        ----------
        models_dict : dict
            {model_name: model_instance}
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ["#2d6a4f", "#52b788", "#1a759f", "#e76f51"]

        for (name, model), color in zip(models_dict.items(), colors):
            y_proba = model.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            auc = roc_auc_score(y_test, y_proba)
            ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})", color=color, lw=2)

        ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Random Classifier")
        ax.set_xlabel("Tasa de Falsos Positivos (FPR)")
        ax.set_ylabel("Tasa de Verdaderos Positivos (TPR / Recall)")
        ax.set_title("Curva ROC — Comparativa de Modelos", fontsize=13, fontweight="bold")
        ax.legend(loc="lower right")
        ax.grid(True, alpha=0.3)

        output_path = self.figures_dir / "roc_curves_comparison.png"
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"ROC curve guardada en: {output_path}")
        return output_path

    def plot_confusion_matrix(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series, model_name: str) -> Path:
        """Genera y guarda la matriz de confusión del modelo champion."""
        cm = confusion_matrix(y_test, model.predict(X_test))
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(
            cm, annot=True, fmt="d", cmap="Greens",
            xticklabels=["Activo", "Churn"],
            yticklabels=["Activo", "Churn"],
            ax=ax,
        )
        ax.set_xlabel("Predicción", fontsize=12)
        ax.set_ylabel("Real", fontsize=12)
        ax.set_title(f"Matriz de Confusión — {model_name}", fontsize=13, fontweight="bold")

        output_path = self.figures_dir / "confusion_matrix_best.png"
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Confusion matrix guardada en: {output_path}")
        return output_path

    def plot_precision_recall_curve(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series, model_name: str) -> Path:
        """Genera la curva Precision-Recall para diagnóstico de threshold."""
        y_proba = model.predict_proba(X_test)[:, 1]
        precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(recall, precision, color="#2d6a4f", lw=2, label=f"{model_name}")
        ax.set_xlabel("Recall", fontsize=12)
        ax.set_ylabel("Precisión", fontsize=12)
        ax.set_title("Curva Precision-Recall — Análisis de Umbral", fontsize=13, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)

        output_path = self.figures_dir / "precision_recall_curve.png"
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Precision-Recall curve guardada en: {output_path}")
        return output_path

    def generate_metrics_markdown(self, cv_results: dict, test_metrics: dict) -> str:
        """
        Genera el contenido Markdown del archivo reports/metrics.md.

        Retorna
        -------
        str
            Contenido formateado listo para escribir en metrics.md.
        """
        lines = [
            "# 📊 Métricas del Modelo de Predicción de Churn",
            "",
            f"> **Modelo Seleccionado:** {test_metrics['model_name']}  ",
            f"> **Criterio de selección:** Maximizar **Recall** (minimizar falsos negativos)  ",
            "",
            "## 🏆 Comparativa de Modelos (Validación Cruzada — 5 Folds)",
            "",
            "| Modelo | Recall (CV) ± Std | F1 (CV) | AUC (CV) | Accuracy (CV) |",
            "|--------|-------------------|---------|----------|---------------|",
        ]
        for name, m in cv_results.items():
            lines.append(
                f"| {name} | {m['recall_mean']:.4f} ± {m['recall_std']:.3f} | "
                f"{m['f1_mean']:.4f} | {m['auc_mean']:.4f} | {m['accuracy_mean']:.4f} |"
            )

        lines += [
            "",
            "## ✅ Métricas Finales (Test Set — 20% holdout)",
            "",
            "| Métrica | Valor |",
            "|---------|-------|",
            f"| **Recall** *(prioritaria)* | **{test_metrics['recall']:.4f}** |",
            f"| F1 Score | {test_metrics['f1']:.4f} |",
            f"| ROC-AUC | {test_metrics['auc']:.4f} |",
            f"| Accuracy | {test_metrics['accuracy']:.4f} |",
            "",
            "## 🔍 Interpretación",
            "",
            f"- Un Recall de **{test_metrics['recall']:.1%}** significa que el modelo detecta correctamente "
            f"ese porcentaje de clientes que abandonarán.",
            "- Los **falsos negativos** (clientes en riesgo no detectados) son el error más costoso en churn.",
            "- La curva Precision-Recall permite ajustar el umbral de decisión según el presupuesto de retención.",
        ]
        return "\n".join(lines)

    @property
    def metrics(self) -> Optional[dict]:
        """Métricas de la última evaluación."""
        return self._metrics
