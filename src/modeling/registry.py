"""
src.modeling.registry — Registro y Versionado de Modelos
=========================================================
Responsabilidad única: guardar, versionar y cargar artefactos
de modelos entrenados con metadata completa.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import joblib
import pandas as pd

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Gestiona el ciclo de vida de los modelos entrenados.

    Estructura de carpetas generada:
    models/
    ├── registry/
    │   ├── v1.0/
    │   │   ├── xgboost_churn_model.pkl
    │   │   ├── scaler.pkl
    │   │   ├── feature_names.json
    │   │   └── model_metadata.json
    │   └── v2.0/
    └── champion/
        └── champion_model.pkl

    Parámetros
    ----------
    registry_dir : str | Path
        Directorio raíz del registry. Por defecto 'models/registry'.
    champion_dir : str | Path
        Directorio del modelo activo. Por defecto 'models/champion'.
    """

    def __init__(
        self,
        registry_dir: str | Path = "models/registry",
        champion_dir: str | Path = "models/champion",
    ) -> None:
        self.registry_dir = Path(registry_dir)
        self.champion_dir = Path(champion_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.champion_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        model: Any,
        model_name: str,
        features: list[str],
        metrics: dict,
        scaler: Optional[Any] = None,
        version: Optional[str] = None,
        make_champion: bool = True,
    ) -> Path:
        """
        Guarda el modelo, scaler y metadata en el registry.

        Parámetros
        ----------
        model : Any
            Modelo entrenado a serializar.
        model_name : str
            Nombre del modelo (ej. 'XGBoost').
        features : list[str]
            Lista de features usadas en el entrenamiento.
        metrics : dict
            Métricas de evaluación del modelo.
        scaler : Any, opcional
            Scaler ajustado. Si se pasa, se guarda junto al modelo.
        version : str, opcional
            Versión del modelo. Si None, se auto-genera con timestamp.
        make_champion : bool
            Si True, copia el modelo al directorio champion. Por defecto True.

        Retorna
        -------
        Path
            Ruta del directorio de la versión guardada.
        """
        if version is None:
            version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        version_dir = self.registry_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)

        # Guardar modelo
        model_filename = f"{model_name.lower()}_churn_model.pkl"
        model_path = version_dir / model_filename
        joblib.dump(model, model_path)
        logger.info(f"Modelo guardado: {model_path}")

        # Guardar scaler
        if scaler is not None:
            scaler_path = version_dir / "scaler.pkl"
            joblib.dump(scaler, scaler_path)
            logger.info(f"Scaler guardado: {scaler_path}")

        # Guardar feature names
        features_path = version_dir / "feature_names.json"
        with open(features_path, "w") as f:
            json.dump({"features": features}, f, indent=2)

        # Guardar metadata
        metadata = {
            "version": version,
            "model_name": model_name,
            "saved_at": datetime.now().isoformat(),
            "features": features,
            "metrics": metrics,
            "files": {
                "model": model_filename,
                "scaler": "scaler.pkl" if scaler is not None else None,
                "features": "feature_names.json",
            },
        }
        metadata_path = version_dir / "model_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        logger.info(f"Metadata guardada: {metadata_path}")

        # Promover a champion
        if make_champion:
            self._promote_to_champion(model, model_name, version)

        logger.info(f"✅ Modelo {model_name} guardado como versión '{version}'")
        return version_dir

    def _promote_to_champion(self, model: Any, model_name: str, version: str) -> None:
        """Copia el modelo como champion activo."""
        champion_path = self.champion_dir / "champion_model.pkl"
        joblib.dump(model, champion_path)

        champion_info = {
            "model_name": model_name,
            "version": version,
            "promoted_at": datetime.now().isoformat(),
        }
        with open(self.champion_dir / "champion_info.json", "w") as f:
            json.dump(champion_info, f, indent=2)
        logger.info(f"🏆 Modelo promovido a champion: {champion_path}")

    def load_champion(self) -> tuple[Any, dict]:
        """
        Carga el modelo champion activo.

        Retorna
        -------
        tuple[Any, dict]
            (modelo, info del champion)
        """
        champion_path = self.champion_dir / "champion_model.pkl"
        info_path = self.champion_dir / "champion_info.json"

        if not champion_path.exists():
            raise FileNotFoundError(
                f"No hay modelo champion en {self.champion_dir}. "
                "Ejecuta run_training_pipeline.py primero."
            )

        model = joblib.load(champion_path)
        info = json.loads(info_path.read_text()) if info_path.exists() else {}
        logger.info(f"Champion cargado: {info.get('model_name', 'Desconocido')} v{info.get('version', '?')}")
        return model, info

    def load_version(self, version: str) -> tuple[Any, dict]:
        """Carga una versión específica del registry."""
        version_dir = self.registry_dir / version
        if not version_dir.exists():
            raise FileNotFoundError(f"Versión '{version}' no encontrada en el registry.")

        metadata_path = version_dir / "model_metadata.json"
        metadata = json.loads(metadata_path.read_text())
        model_file = version_dir / metadata["files"]["model"]
        model = joblib.load(model_file)
        logger.info(f"Versión '{version}' cargada: {metadata['model_name']}")
        return model, metadata

    def list_versions(self) -> pd.DataFrame:
        """Lista todas las versiones disponibles en el registry."""
        versions = []
        for version_dir in sorted(self.registry_dir.iterdir()):
            if version_dir.is_dir():
                meta_path = version_dir / "model_metadata.json"
                if meta_path.exists():
                    meta = json.loads(meta_path.read_text())
                    versions.append({
                        "version": meta.get("version"),
                        "model_name": meta.get("model_name"),
                        "saved_at": meta.get("saved_at"),
                        "recall": meta.get("metrics", {}).get("recall"),
                        "f1": meta.get("metrics", {}).get("f1"),
                        "auc": meta.get("metrics", {}).get("auc"),
                    })
        return pd.DataFrame(versions) if versions else pd.DataFrame()
