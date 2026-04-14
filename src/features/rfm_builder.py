"""
src.features.rfm_builder — Construcción de Métricas RFM
========================================================
Responsabilidad única: calcular Recency, Frequency y Monetary
a partir del dataset de transacciones limpio.
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class RFMBuilder:
    """
    Construye las métricas RFM (Recency, Frequency, Monetary) por cliente.

    Recency   → Días desde la última compra (menor = más reciente = mejor).
    Frequency → Número de facturas únicas del cliente.
    Monetary  → Suma total gastada por el cliente.

    Parámetros
    ----------
    snapshot_date : datetime | None
        Fecha de referencia para calcular Recency. Si None, usa
        max(InvoiceDate) + 1 día del dataset.
    apply_log_transform : bool
        Si True, aplica log1p a Monetary y Frequency para reducir
        el impacto de outliers. Por defecto True.
    clip_quantile : float
        Percentil al que se clipa Monetary antes de la transformación.
        Por defecto 0.99. Set a None para desactivar.
    """

    def __init__(
        self,
        snapshot_date: Optional[dt.datetime] = None,
        apply_log_transform: bool = True,
        clip_quantile: float = 0.99,
    ) -> None:
        self.snapshot_date = snapshot_date
        self.apply_log_transform = apply_log_transform
        self.clip_quantile = clip_quantile
        self._snapshot_used: Optional[dt.datetime] = None

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Construye el DataFrame RFM agregado por cliente.

        Parámetros
        ----------
        df : pd.DataFrame
            Dataset de transacciones limpio con columnas:
            'Customer ID', 'InvoiceDate', 'Invoice', 'TotalSum'.

        Retorna
        -------
        pd.DataFrame
            DataFrame con columnas: Customer ID, Recency,
            Frequency, Monetary. Índice: enteros secuenciales.
        """
        required_cols = {"Customer ID", "InvoiceDate", "Invoice", "TotalSum"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Columnas faltantes para RFM: {missing}")

        # Definir fecha snapshot
        if self.snapshot_date is None:
            snapshot = df["InvoiceDate"].max() + dt.timedelta(days=1)
        else:
            snapshot = self.snapshot_date
        self._snapshot_used = snapshot
        logger.info(f"Snapshot date para Recency: {snapshot.date()}")

        # Agregación por cliente
        rfm = (
            df.groupby("Customer ID")
            .agg(
                Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
                Frequency=("Invoice", "nunique"),
                Monetary=("TotalSum", "sum"),
            )
            .reset_index()
        )

        logger.info(
            f"RFM construido: {len(rfm):,} clientes únicos | "
            f"Recency media: {rfm['Recency'].mean():.0f}d | "
            f"Monetary media: £{rfm['Monetary'].mean():.2f}"
        )

        # Tratamiento de outliers en Monetary
        if self.clip_quantile is not None:
            cap = rfm["Monetary"].quantile(self.clip_quantile)
            outliers = (rfm["Monetary"] > cap).sum()
            if outliers > 0:
                logger.debug(f"Clipeando {outliers} outliers de Monetary al p{int(self.clip_quantile*100)}: £{cap:.2f}")
            rfm["Monetary"] = rfm["Monetary"].clip(upper=cap)

        # Transformación logarítmica
        if self.apply_log_transform:
            rfm["Monetary_Log"] = np.log1p(rfm["Monetary"])
            rfm["Frequency_Log"] = np.log1p(rfm["Frequency"])
            logger.debug("Log1p aplicado a Monetary y Frequency (columnas '_Log' añadidas).")

        return rfm

    @property
    def snapshot_used(self) -> Optional[dt.datetime]:
        """Retorna la fecha snapshot utilizada en el último build."""
        return self._snapshot_used
