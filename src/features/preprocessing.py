"""
src.features.preprocessing — Limpieza de Transacciones
=======================================================
Responsabilidad única: limpiar el DataFrame de transacciones raw,
eliminar registros inválidos y preparar datos para la construcción de RFM.
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TransactionPreprocessor:
    """
    Limpia el dataset de transacciones Online Retail II.

    Operaciones que realiza:
    1. Filtra registros sin Customer ID
    2. Filtra facturas canceladas (Invoice empieza con 'C')
    3. Elimina precios y cantidades negativos o cero
    4. Calcula TotalSum = Quantity * Price
    5. Convierte tipos de datos correctamente

    Parámetros
    ----------
    min_price : float
        Precio mínimo aceptable por unidad. Por defecto 0.01.
    min_quantity : int
        Cantidad mínima aceptable. Por defecto 1.
    drop_cancelled : bool
        Si True, elimina facturas canceladas. Por defecto True.
    """

    def __init__(
        self,
        min_price: float = 0.01,
        min_quantity: int = 1,
        drop_cancelled: bool = True,
    ) -> None:
        self.min_price = min_price
        self.min_quantity = min_quantity
        self.drop_cancelled = drop_cancelled
        self._stats: dict = {}

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica todas las transformaciones de limpieza al DataFrame.

        Parámetros
        ----------
        df : pd.DataFrame
            DataFrame raw del dataset Online Retail II.

        Retorna
        -------
        pd.DataFrame
            DataFrame limpio listo para la construcción de RFM.
        """
        initial_rows = len(df)
        logger.info(f"Iniciando preprocesamiento: {initial_rows:,} transacciones")

        df = df.copy()

        # 1. Asegurar tipos de datos
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
        df["Customer ID"] = df["Customer ID"].astype(str).str.strip()
        df["Invoice"] = df["Invoice"].astype(str).str.strip()

        # 2. Eliminar registros sin Customer ID
        mask_cid = df["Customer ID"].notnull() & (df["Customer ID"] != "nan") & (df["Customer ID"] != "")
        df = df[mask_cid].copy()
        logger.debug(f"  Tras filtrar Customer ID nulos: {len(df):,} filas")

        # 3. Eliminar facturas canceladas
        if self.drop_cancelled:
            df = df[~df["Invoice"].str.startswith("C", na=False)].copy()
            logger.debug(f"  Tras eliminar cancelaciones: {len(df):,} filas")

        # 4. Eliminar precios y cantidades inválidos
        df = df[df["Price"] >= self.min_price].copy()
        df = df[df["Quantity"] >= self.min_quantity].copy()
        logger.debug(f"  Tras filtrar precio/cantidad mínimos: {len(df):,} filas")

        # 5. Eliminar fechas nulas (resultado del coerce)
        df = df[df["InvoiceDate"].notnull()].copy()

        # 6. Calcular TotalSum
        df["TotalSum"] = df["Quantity"] * df["Price"]

        final_rows = len(df)
        removed = initial_rows - final_rows
        self._stats = {
            "initial_rows": initial_rows,
            "final_rows": final_rows,
            "removed_rows": removed,
            "removal_pct": removed / initial_rows * 100,
        }
        logger.info(
            f"Preprocesamiento completo: {final_rows:,} filas válidas "
            f"(removidas: {removed:,} = {self._stats['removal_pct']:.1f}%)"
        )
        return df

    @property
    def stats(self) -> dict:
        """Retorna estadísticas del último procesamiento."""
        return self._stats
