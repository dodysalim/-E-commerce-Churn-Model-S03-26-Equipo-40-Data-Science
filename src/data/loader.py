"""
src.data.loader — Carga Eficiente del Dataset
==============================================
Responsabilidad única: cargar el dataset Online Retail II de forma
eficiente, con soporte para chunking en datasets grandes.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Columnas esperadas en el dataset original
EXPECTED_COLUMNS = [
    "Invoice", "StockCode", "Description",
    "Quantity", "InvoiceDate", "Price",
    "Customer ID", "Country",
]


class DataLoader:
    """
    Carga el dataset Online Retail II con validación de esquema básica.

    Parámetros
    ----------
    file_path : str | Path
        Ruta al archivo CSV del dataset raw.
    encoding : str
        Codificación del archivo. Por defecto 'utf-8'.
    """

    def __init__(self, file_path: str | Path, encoding: str = "utf-8") -> None:
        self.file_path = Path(file_path)
        self.encoding = encoding
        self._df: Optional[pd.DataFrame] = None

    def load(self, usecols: Optional[list[str]] = None) -> pd.DataFrame:
        """
        Carga el dataset completo en memoria.

        Parámetros
        ----------
        usecols : list[str], opcional
            Subconjunto de columnas a cargar. Por defecto carga todas.

        Retorna
        -------
        pd.DataFrame
            DataFrame con los datos cargados.

        Raises
        ------
        FileNotFoundError
            Si el archivo no existe en la ruta especificada.
        ValueError
            Si el archivo está vacío o las columnas no coinciden.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Dataset no encontrado: {self.file_path}\n"
                f"Asegúrate de que 'online_retail_II.csv' está en data/raw/"
            )

        cols_to_load = usecols or EXPECTED_COLUMNS
        logger.info(f"Cargando dataset: {self.file_path} ({self.file_path.stat().st_size / 1e6:.1f} MB)")

        try:
            df = pd.read_csv(
                self.file_path,
                usecols=cols_to_load,
                encoding=self.encoding,
                low_memory=False,
                dtype={"Invoice": str, "StockCode": str, "Customer ID": str},
                parse_dates=["InvoiceDate"],
            )
        except UnicodeDecodeError:
            logger.warning("UTF-8 falló, intentando con latin-1...")
            df = pd.read_csv(
                self.file_path,
                usecols=cols_to_load,
                encoding="latin-1",
                low_memory=False,
                dtype={"Invoice": str, "StockCode": str, "Customer ID": str},
                parse_dates=["InvoiceDate"],
            )

        if df.empty:
            raise ValueError("El dataset está vacío.")

        logger.info(f"Dataset cargado: {len(df):,} filas × {len(df.columns)} columnas")
        self._df = df
        return df

    def load_chunks(self, chunksize: int = 100_000):
        """
        Carga el dataset en chunks (útil para memoria limitada).

        Parámetros
        ----------
        chunksize : int
            Número de filas por chunk. Por defecto 100,000.

        Yields
        ------
        pd.DataFrame
            Chunks del dataset.
        """
        logger.info(f"Cargando en chunks de {chunksize:,} filas...")
        for i, chunk in enumerate(
            pd.read_csv(
                self.file_path,
                chunksize=chunksize,
                encoding=self.encoding,
                low_memory=False,
                dtype={"Invoice": str, "StockCode": str, "Customer ID": str},
                parse_dates=["InvoiceDate"],
            )
        ):
            logger.debug(f"Procesando chunk {i + 1} ({len(chunk):,} filas)")
            yield chunk

    @property
    def shape(self) -> Optional[tuple[int, int]]:
        """Retorna las dimensiones del dataset si ya fue cargado."""
        return self._df.shape if self._df is not None else None

    def get_date_range(self) -> dict:
        """Retorna el rango de fechas del dataset cargado."""
        if self._df is None:
            raise RuntimeError("Primero ejecuta .load()")
        return {
            "min_date": self._df["InvoiceDate"].min(),
            "max_date": self._df["InvoiceDate"].max(),
            "days_span": (self._df["InvoiceDate"].max() - self._df["InvoiceDate"].min()).days,
        }
