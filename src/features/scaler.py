"""
src.features.scaler — Escalamiento de Features con Persistencia
===============================================================
Responsabilidad única: escalar features numéricas y serializar
el scaler para garantizar la consistencia entre entrenamiento e inferencia.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class FeatureScaler:
    """
    Encapsula el StandardScaler con capacidad de serialización.

    La serialización es crítica en producción: el scaler entrenado
    en el dataset de entrenamiento debe aplicarse en inferencia sin reajuste.

    Parámetros
    ----------
    features : list[str]
        Lista de columnas numéricas a escalar.
    """

    def __init__(self, features: list[str]) -> None:
        self.features = features
        self._scaler: StandardScaler = StandardScaler()
        self._is_fitted: bool = False

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajusta el scaler sobre df y transforma las features.

        Retorna
        -------
        pd.DataFrame
            DataFrame con las features escaladas (in-place en copia).
        """
        df_out = df.copy()
        df_out[self.features] = self._scaler.fit_transform(df[self.features])
        self._is_fitted = True
        logger.info(f"Scaler ajustado sobre {len(self.features)} features: {self.features}")
        return df_out

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica el scaler ya ajustado (para inferencia).

        Raises
        ------
        RuntimeError
            Si el scaler no ha sido ajustado previamente.
        """
        if not self._is_fitted:
            raise RuntimeError("El scaler no ha sido ajustado. Ejecuta fit_transform primero.")
        df_out = df.copy()
        df_out[self.features] = self._scaler.transform(df[self.features])
        return df_out

    def save(self, path: str | Path) -> Path:
        """Serializa el scaler ajustado a disco."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._scaler, path)
        logger.info(f"Scaler guardado en: {path}")
        return path

    @classmethod
    def load(cls, path: str | Path, features: list[str]) -> "FeatureScaler":
        """
        Carga un scaler previamente serializado.

        Retorna
        -------
        FeatureScaler
            Instancia lista para inferencia.
        """
        instance = cls(features=features)
        instance._scaler = joblib.load(path)
        instance._is_fitted = True
        logger.info(f"Scaler cargado desde: {path}")
        return instance

    @property
    def means(self) -> Optional[list[float]]:
        """Retorna las medias aprendidas por feature."""
        if not self._is_fitted:
            return None
        return self._scaler.mean_.tolist()

    @property
    def stds(self) -> Optional[list[float]]:
        """Retorna las desviaciones estándar aprendidas por feature."""
        if not self._is_fitted:
            return None
        return self._scaler.scale_.tolist()
