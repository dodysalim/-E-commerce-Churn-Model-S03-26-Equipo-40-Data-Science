"""
src.data.validator — Validación de Esquema y Calidad de Datos
=============================================================
Responsabilidad única: validar que el DataFrame cargado cumple
con el esquema esperado antes de continuar con el pipeline.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

import pandas as pd

# Suprimir FutureWarning de pandera al importar
os.environ.setdefault("DISABLE_PANDERA_IMPORT_WARNING", "True")

logger = logging.getLogger(__name__)


# ─── Resultado de Validación ─────────────────────────────────────────────────
@dataclass
class ValidationReport:
    """Encapsula el resultado de una validación de datos."""

    passed: bool
    total_rows: int
    null_counts: dict[str, int]
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "✅ PASÓ" if self.passed else "❌ FALLÓ"
        lines = [
            f"=== Validación de Datos: {status} ===",
            f"  Filas totales    : {self.total_rows:,}",
        ]
        if self.null_counts:
            lines.append(f"  Nulos detectados : {self.null_counts}")
        if self.warnings:
            lines.append("  ⚠️  Advertencias:")
            lines.extend(f"     - {w}" for w in self.warnings)
        if self.errors:
            lines.append("  ❌ Errores:")
            lines.extend(f"     - {e}" for e in self.errors)
        return "\n".join(lines)


class DataValidator:
    """
    Valida la calidad y el esquema del DataFrame de transacciones.

    Ejecuta controles de:
    - Columnas requeridas presentes
    - Dataset no vacío
    - Nulos en columnas críticas (InvoiceDate, Invoice)
    - Customer ID nulos (advertencia — se filtran en preprocessing)
    - Precios y cantidades fuera de rango

    Parámetros
    ----------
    raise_on_error : bool
        Si True, lanza una excepción ante errores críticos.
        Si False, solo registra advertencias. Por defecto True.
    """

    CRITICAL_NULL_COLUMNS = ["InvoiceDate", "Invoice"]
    EXPECTED_COLUMNS = [
        "Invoice", "StockCode", "Description",
        "Quantity", "InvoiceDate", "Price",
        "Customer ID", "Country",
    ]

    def __init__(self, raise_on_error: bool = True) -> None:
        self.raise_on_error = raise_on_error

    def validate(self, df: pd.DataFrame) -> ValidationReport:
        """
        Ejecuta todos los controles de validación sobre el DataFrame.

        Parámetros
        ----------
        df : pd.DataFrame
            DataFrame a validar.

        Retorna
        -------
        ValidationReport
            Reporte detallado con resultados de la validación.
        """
        logger.info("Iniciando validación de datos...")
        errors: list[str] = []
        warnings: list[str] = []

        # 1. Columnas esperadas
        missing_cols = [c for c in self.EXPECTED_COLUMNS if c not in df.columns]
        if missing_cols:
            errors.append(f"Columnas faltantes: {missing_cols}")

        # 2. Dataset no vacío
        if df.empty:
            errors.append("El DataFrame está vacío.")

        # 3. Nulos críticos
        null_counts = df.isnull().sum().to_dict()
        for col in self.CRITICAL_NULL_COLUMNS:
            if col in df.columns and null_counts.get(col, 0) > 0:
                errors.append(f"Nulos críticos en '{col}': {null_counts[col]:,}")

        # 4. Customer ID nulos (advertencia — se filtran en preprocessing)
        if "Customer ID" in df.columns:
            cid_nulls = df["Customer ID"].isnull().sum()
            if cid_nulls > 0:
                pct = cid_nulls / len(df) * 100
                warnings.append(
                    f"'Customer ID' tiene {cid_nulls:,} nulos ({pct:.1f}%) "
                    "→ se eliminarán en preprocesamiento."
                )

        # 5. Precios negativos
        if "Price" in df.columns:
            neg_price = (df["Price"] < 0).sum()
            if neg_price > 0:
                warnings.append(
                    f"{neg_price:,} registros con Price < 0 → se eliminarán en preprocesamiento."
                )

        # 6. Cantidades extremas (posibles clientes B2B)
        if "Quantity" in df.columns:
            very_high = (df["Quantity"] > 10_000).sum()
            if very_high > 0:
                warnings.append(
                    f"{very_high:,} registros con Quantity > 10,000 (posibles outliers B2B)."
                )

        # 7. Rango de fechas (informativo)
        if "InvoiceDate" in df.columns and not df["InvoiceDate"].isnull().all():
            min_date = df["InvoiceDate"].min()
            max_date = df["InvoiceDate"].max()
            logger.info(f"Rango de fechas: {min_date} → {max_date}")

        passed = len(errors) == 0
        report = ValidationReport(
            passed=passed,
            total_rows=len(df),
            null_counts={k: int(v) for k, v in null_counts.items() if v > 0},
            warnings=warnings,
            errors=errors,
        )

        logger.info(report.summary())

        if not passed and self.raise_on_error:
            raise ValueError(f"Validación fallida:\n{report.summary()}")

        return report
