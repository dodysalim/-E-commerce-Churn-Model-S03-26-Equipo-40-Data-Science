"""
src.modeling.trainer — Entrenamiento Multi-Modelo con Validación Cruzada
========================================================================
Responsabilidad única: entrenar múltiples modelos, aplicar manejo de
desbalance de clases, y seleccionar el mejor basado en Recall mediante CV.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Entrena, valida y selecciona el mejor modelo para predicción de churn.

    Manejo de desbalance:
    - class_weight='balanced' en RF y LR
    - scale_pos_weight dinámico en XGBoost
    - Validación cruzada estratificada (StratifiedKFold)

    Parámetros
    ----------
    features : list[str]
        Columnas a usar como features de entrenamiento.
    target : str
        Columna objetivo (etiqueta de churn). Por defecto 'CHURN'.
    test_size : float
        Proporción del set de test. Por defecto 0.20.
    cv_folds : int
        Número de folds para validación cruzada. Por defecto 5.
    random_state : int
        Semilla de aleatoriedad para reproducibilidad. Por defecto 42.
    primary_metric : str
        Métrica de selección del mejor modelo. Por defecto 'recall'.
    """

    def __init__(
        self,
        features: list[str],
        target: str = "CHURN",
        test_size: float = 0.20,
        cv_folds: int = 5,
        random_state: int = 42,
        primary_metric: str = "recall",
    ) -> None:
        self.features = features
        self.target = target
        self.test_size = test_size
        self.cv_folds = cv_folds
        self.random_state = random_state
        self.primary_metric = primary_metric

        self.best_model: Optional[Any] = None
        self.best_model_name: str = ""
        self.X_train: Optional[pd.DataFrame] = None
        self.X_test: Optional[pd.DataFrame] = None
        self.y_train: Optional[pd.Series] = None
        self.y_test: Optional[pd.Series] = None
        self._cv_results: dict = {}

    def _build_models(self, scale_pos_weight: float) -> dict[str, Any]:
        """Construye los modelos con manejo de desbalance."""
        return {
            "RandomForest": RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            "LogisticRegression": LogisticRegression(
                max_iter=1000,
                solver="lbfgs",
                class_weight="balanced",
                random_state=self.random_state,
            ),
            "XGBoost": XGBClassifier(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                eval_metric="logloss",
                scale_pos_weight=scale_pos_weight,
                random_state=self.random_state,
                verbosity=0,
            ),
        }

    def fit(self, df: pd.DataFrame) -> "ModelTrainer":
        """
        Divide los datos, aplica validación cruzada y entrena el mejor modelo.

        Parámetros
        ----------
        df : pd.DataFrame
            DataFrame completo con features y target.

        Retorna
        -------
        ModelTrainer
            La instancia entrenada (para encadenamiento).
        """
        X = df[self.features]
        y = df[self.target]

        # Split estratificado
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        logger.info(
            f"Split estratificado: Train={len(self.X_train):,} | Test={len(self.X_test):,} | "
            f"Churn train: {self.y_train.mean():.1%}"
        )

        # Calcular scale_pos_weight para XGBoost
        neg = (self.y_train == 0).sum()
        pos = (self.y_train == 1).sum()
        scale_pos_weight = neg / pos if pos > 0 else 1.0
        logger.debug(f"XGBoost scale_pos_weight={scale_pos_weight:.2f}")

        models = self._build_models(scale_pos_weight)
        cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)

        best_score = -np.inf
        logger.info(f"\n{'─'*60}")
        logger.info(f"  Evaluación de Modelos ({self.cv_folds}-Fold CV) — Prioridad: {self.primary_metric.upper()}")
        logger.info(f"{'─'*60}")

        for name, model in models.items():
            cv_result = cross_validate(
                model, self.X_train, self.y_train,
                cv=cv,
                scoring=["recall", "f1", "roc_auc", "accuracy"],
                n_jobs=-1,
                error_score="raise",
            )
            self._cv_results[name] = {
                "recall_mean": cv_result["test_recall"].mean(),
                "recall_std": cv_result["test_recall"].std(),
                "f1_mean": cv_result["test_f1"].mean(),
                "auc_mean": cv_result["test_roc_auc"].mean(),
                "accuracy_mean": cv_result["test_accuracy"].mean(),
            }
            score = self._cv_results[name][f"{self.primary_metric}_mean"]
            logger.info(
                f"  {name:<22} Recall={cv_result['test_recall'].mean():.4f}±{cv_result['test_recall'].std():.3f} | "
                f"F1={cv_result['test_f1'].mean():.4f} | AUC={cv_result['test_roc_auc'].mean():.4f}"
            )

            if score > best_score:
                best_score = score
                self.best_model_name = name
                self.best_model = model

        logger.info(f"{'─'*60}")
        logger.info(f"  ✅ Mejor modelo: {self.best_model_name} ({self.primary_metric}={best_score:.4f})")
        logger.info(f"{'─'*60}\n")

        # Reentrenar sobre todo el train set
        self.best_model.fit(self.X_train, self.y_train)
        return self

    @property
    def cv_results(self) -> dict:
        """Resultados de validación cruzada para cada modelo."""
        return self._cv_results
