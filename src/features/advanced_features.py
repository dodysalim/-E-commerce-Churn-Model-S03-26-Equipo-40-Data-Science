"""
src.features.advanced_features — Features Avanzadas Más Allá de RFM
====================================================================
Responsabilidad única: calcular características adicionales que
enriquecen el perfil de comportamiento del cliente.

Features generadas:
  - AvgTicket         : Ticket promedio por factura
  - DaysBetweenPurchases : Promedio de días entre compras consecutivas
  - MonetaryStdDev    : Desviación estándar del gasto (consistencia)
  - UniqueProducts    : Número de productos únicos comprados
  - PeakHourBuyer     : Si el cliente compra en horario pico (10-14h)
  - UniqueCountries   : Número de países desde donde compra
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class AdvancedFeatureEngineer:
    """
    Genera features adicionales a partir del dataset de transacciones limpio
    y las une al DataFrame RFM.

    Parámetros
    ----------
    peak_hours : tuple[int, int]
        Rango de horas que define el 'horario pico'. Por defecto (10, 14).
    """

    def __init__(self, peak_hours: tuple[int, int] = (10, 14)) -> None:
        self.peak_hours = peak_hours

    def build(self, transactions_df: pd.DataFrame, rfm_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula features avanzadas y las une al DataFrame RFM.

        Parámetros
        ----------
        transactions_df : pd.DataFrame
            Dataset de transacciones limpio.
        rfm_df : pd.DataFrame
            DataFrame RFM ya construido con columna 'Customer ID'.

        Retorna
        -------
        pd.DataFrame
            rfm_df enriquecido con las nuevas features.
        """
        logger.info("Calculando features avanzadas de comportamiento...")
        advanced = self._compute_advanced(transactions_df)
        enriched = rfm_df.merge(advanced, on="Customer ID", how="left")
        # Rellenar NaN para clientes sin suficiente historial
        enriched["DaysBetweenPurchases"] = enriched["DaysBetweenPurchases"].fillna(
            enriched["Recency"]
        )
        enriched["MonetaryStdDev"] = enriched["MonetaryStdDev"].fillna(0)
        logger.info(f"Features avanzadas añadidas: {list(advanced.columns[1:])}")
        return enriched

    def _compute_advanced(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todas las features avanzadas del dataset de transacciones."""

        # AvgTicket: Monetario promedio por factura
        avg_ticket = (
            df.groupby(["Customer ID", "Invoice"])["TotalSum"]
            .sum()
            .reset_index()
            .groupby("Customer ID")["TotalSum"]
            .mean()
            .rename("AvgTicket")
        )

        # DaysBetweenPurchases: Promedio de días entre compras consecutivas
        def _avg_days_between(dates: pd.Series) -> float:
            sorted_dates = dates.sort_values()
            if len(sorted_dates) < 2:
                return np.nan
            diffs = sorted_dates.diff().dropna().dt.days
            return diffs.mean()

        days_between = (
            df.groupby("Customer ID")["InvoiceDate"]
            .apply(_avg_days_between)
            .rename("DaysBetweenPurchases")
        )

        # MonetaryStdDev: Varianza del gasto por factura
        monetary_std = (
            df.groupby(["Customer ID", "Invoice"])["TotalSum"]
            .sum()
            .reset_index()
            .groupby("Customer ID")["TotalSum"]
            .std()
            .fillna(0)
            .rename("MonetaryStdDev")
        )

        # UniqueProducts: Número de StockCodes únicos
        unique_products = (
            df.groupby("Customer ID")["StockCode"]
            .nunique()
            .rename("UniqueProducts")
        )

        # PeakHourBuyer: Proporción de compras en horario pico
        df_with_hour = df.copy()
        df_with_hour["Hour"] = df_with_hour["InvoiceDate"].dt.hour
        peak_start, peak_end = self.peak_hours
        df_with_hour["IsPeak"] = (
            (df_with_hour["Hour"] >= peak_start) & (df_with_hour["Hour"] < peak_end)
        ).astype(int)
        peak_buyer = (
            df_with_hour.groupby("Customer ID")["IsPeak"]
            .mean()
            .rename("PeakHourBuyer")
        )

        # Unir todo
        advanced = (
            avg_ticket.reset_index()
            .merge(days_between.reset_index(), on="Customer ID", how="outer")
            .merge(monetary_std.reset_index(), on="Customer ID", how="outer")
            .merge(unique_products.reset_index(), on="Customer ID", how="outer")
            .merge(peak_buyer.reset_index(), on="Customer ID", how="outer")
        )
        return advanced
