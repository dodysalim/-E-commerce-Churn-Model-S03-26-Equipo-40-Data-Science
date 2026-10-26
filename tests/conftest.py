"""
tests/conftest.py — Fixtures Compartidos para la Suite de Tests
==============================================================
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Asegurar que src/ sea importable en los tests
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ─── Fixtures de Dataset Mini ────────────────────────────────────────────────
@pytest.fixture(scope="session")
def sample_transactions():
    """Dataset mini de transacciones para tests (100 filas)."""
    np.random.seed(42)
    n = 100
    customers = [f"C{i:04d}" for i in range(1, 21)]  # 20 clientes únicos

    return pd.DataFrame({
        "Invoice": [f"INV{i:05d}" for i in range(n)],
        "StockCode": np.random.choice(["85123A", "71053", "84406B"], n),
        "Description": np.random.choice(["WHITE HANGING HEART", "WHITE METAL LANTERN"], n),
        "Quantity": np.random.randint(1, 50, n),
        "InvoiceDate": pd.date_range(start="2010-01-01", periods=n, freq="3D"),
        "Price": np.random.uniform(0.5, 15.0, n).round(2),
        "Customer ID": np.random.choice(customers, n),
        "Country": np.random.choice(["United Kingdom", "France", "Germany"], n),
    })


@pytest.fixture(scope="session")
def sample_rfm():
    """DataFrame RFM sintético de 50 clientes para tests."""
    np.random.seed(42)
    n = 50
    return pd.DataFrame({
        "Customer ID": [f"C{i:04d}" for i in range(1, n + 1)],
        "Recency": np.random.randint(1, 365, n),
        "Frequency": np.random.randint(1, 50, n),
        "Monetary": np.random.uniform(10.0, 5000.0, n).round(2),
    })


@pytest.fixture(scope="session")
def sample_rfm_with_churn(sample_rfm):
    """RFM con etiqueta de churn (threshold = 90 días)."""
    df = sample_rfm.copy()
    df["CHURN"] = (df["Recency"] > 90).astype(int)
    return df


@pytest.fixture(scope="session")
def sample_final_df(sample_rfm_with_churn):
    """DataFrame final con todas las columnas del pipeline."""
    df = sample_rfm_with_churn.copy()
    np.random.seed(42)
    n = len(df)
    df["ChurnProbability"] = np.random.uniform(0, 1, n).round(4)
    df["RiskSegment"] = pd.cut(
        df["ChurnProbability"],
        bins=[0, 0.4, 0.7, 1.0],
        labels=["Estable (Riesgo Bajo)", "Riesgo Medio", "Riesgo Muy Alto"],
    ).astype(str)
    df["CustomerLevel"] = np.random.choice(
        ["VIP / Champion", "Leales / Prometedores", "En Riesgo / Perdidos"], n
    )
    df["RFM_Score"] = np.random.randint(3, 13, n)
    return df
