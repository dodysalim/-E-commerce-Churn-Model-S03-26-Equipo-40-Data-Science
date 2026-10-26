"""
tests/unit/test_preprocessing.py — Tests del TransactionPreprocessor
"""
import pandas as pd
import pytest

from src.features.preprocessing import TransactionPreprocessor


@pytest.mark.unit
class TestTransactionPreprocessor:
    """Tests unitarios para TransactionPreprocessor."""

    def test_removes_null_customer_ids(self, sample_transactions):
        """El preprocessor debe eliminar transacciones sin Customer ID."""
        df = sample_transactions.copy()
        # Inyectar nulos
        df.loc[:5, "Customer ID"] = None
        preprocessor = TransactionPreprocessor()
        result = preprocessor.fit_transform(df)
        assert result["Customer ID"].isnull().sum() == 0

    def test_removes_cancelled_invoices(self, sample_transactions):
        """Facturas con 'C' al inicio deben eliminarse."""
        df = sample_transactions.copy()
        df.loc[0, "Invoice"] = "C12345"
        preprocessor = TransactionPreprocessor(drop_cancelled=True)
        result = preprocessor.fit_transform(df)
        assert not result["Invoice"].str.startswith("C").any()

    def test_cancelled_invoices_kept_when_disabled(self, sample_transactions):
        """Si drop_cancelled=False, las facturas canceladas se conservan."""
        df = sample_transactions.copy()
        df.loc[0, "Invoice"] = "C12345"
        preprocessor = TransactionPreprocessor(drop_cancelled=False)
        result = preprocessor.fit_transform(df)
        # Debe haber al menos una factura con C (la que añadimos)
        assert result["Invoice"].str.startswith("C").any()

    def test_removes_negative_prices(self, sample_transactions):
        """Registros con Price < min_price deben eliminarse."""
        df = sample_transactions.copy()
        df.loc[0, "Price"] = -1.0
        preprocessor = TransactionPreprocessor(min_price=0.01)
        result = preprocessor.fit_transform(df)
        assert (result["Price"] >= 0.01).all()

    def test_totalsum_column_created(self, sample_transactions):
        """La columna TotalSum = Quantity * Price debe existir."""
        preprocessor = TransactionPreprocessor()
        result = preprocessor.fit_transform(sample_transactions)
        assert "TotalSum" in result.columns
        assert (result["TotalSum"] >= 0).all()

    def test_stats_populated_after_transform(self, sample_transactions):
        """Las estadísticas de procesamiento deben estar disponibles."""
        preprocessor = TransactionPreprocessor()
        preprocessor.fit_transform(sample_transactions)
        stats = preprocessor.stats
        assert "initial_rows" in stats
        assert "final_rows" in stats
        assert stats["final_rows"] <= stats["initial_rows"]

    def test_returns_dataframe(self, sample_transactions):
        """El resultado debe ser un DataFrame."""
        preprocessor = TransactionPreprocessor()
        result = preprocessor.fit_transform(sample_transactions)
        assert isinstance(result, pd.DataFrame)
