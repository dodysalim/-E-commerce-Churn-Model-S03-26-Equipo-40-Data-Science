"""
src.data.versioner — Trazabilidad del Dataset
=============================================
Responsabilidad única: generar un hash del dataset para asegurar
que el pipeline siempre trabaja con la misma versión de datos.
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class DataVersioner:
    """
    Genera y verifica hashes del dataset para garantizar reproducibilidad.

    Ejemplo de uso
    --------------
    >>> versioner = DataVersioner(file_path="data/raw/online_retail_II.csv")
    >>> version_info = versioner.generate_version_info()
    >>> versioner.save_version_info(version_info, "data/raw/dataset_version.json")
    """

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def compute_file_hash(self, algorithm: str = "sha256", chunk_size: int = 65536) -> str:
        """
        Calcula el hash del archivo para detectar cambios en el dataset.

        Parámetros
        ----------
        algorithm : str
            Algoritmo de hashing ('sha256', 'md5'). Por defecto 'sha256'.
        chunk_size : int
            Tamaño de los chunks para leer el archivo. Por defecto 65536 bytes.

        Retorna
        -------
        str
            Hash hexadecimal del archivo.
        """
        h = hashlib.new(algorithm)
        with open(self.file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()

    def generate_version_info(self) -> dict:
        """
        Genera metadatos de versión del dataset.

        Retorna
        -------
        dict
            Diccionario con hash, tamaño y fecha de modificación.
        """
        from datetime import datetime

        stat = self.file_path.stat()
        file_hash = self.compute_file_hash()

        version_info = {
            "file_name": self.file_path.name,
            "file_path": str(self.file_path),
            "sha256_hash": file_hash,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / 1e6, 2),
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "generated_at": datetime.now().isoformat(),
        }

        logger.info(f"Dataset version: SHA256={file_hash[:16]}... | Tamaño={version_info['size_mb']} MB")
        return version_info

    def save_version_info(self, version_info: dict, output_path: str | Path) -> None:
        """Guarda la información de versión en un archivo JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(version_info, f, indent=2)
        logger.info(f"Versión del dataset guardada en: {output_path}")

    def verify_dataset(self, expected_hash: str) -> bool:
        """
        Verifica si el dataset actual coincide con un hash esperado.

        Retorna
        -------
        bool
            True si el hash coincide, False si el dataset cambió.
        """
        current_hash = self.compute_file_hash()
        matches = current_hash == expected_hash
        if not matches:
            logger.warning(
                f"⚠️ DATASET MODIFICADO: El hash actual ({current_hash[:16]}...) "
                f"no coincide con el esperado ({expected_hash[:16]}...)"
            )
        else:
            logger.info("✅ Dataset verificado: sin cambios.")
        return matches
