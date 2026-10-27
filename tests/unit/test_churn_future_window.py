"""
tests/unit/test_churn_future_window.py — Etiqueta de churn por ventana futura
"""
import pandas as pd
import pytest

from src.labeling.churn_label import ChurnLabeler


@pytest.fixture
def transactions():
    """C001 compra antes y después del corte; C002 solo antes; C003 compra en el borde."""
    return pd.DataFrame({
        "Customer ID": ["C001", "C001", "C002", "C003", "C003"],
        "InvoiceDate": pd.to_datetime([
            "2011-06-01",  # antes del corte
            "2011-10-15",  # dentro de la ventana (corte 2011-09-09, horizonte 90d)
            "2011-06-10",  # solo antes del corte
            "2011-09-09",  # justo en el corte: no cuenta como futuro
            "2011-12-08",  # después de la ventana (corte + 90 días = 2011-12-08)
        ]),
    })


@pytest.fixture
def rfm_observed():
    return pd.DataFrame({
        "Customer ID": ["C001", "C002", "C003"],
        "Recency": [100, 120, 1],
        "Frequency": [2, 1, 2],
        "Monetary": [200.0, 50.0, 300.0],
    })


@pytest.mark.unit
class TestFutureWindowLabel:
    """La etiqueta no debe depender de Recency."""

    def test_buyer_inside_window_is_active(self, transactions, rfm_observed):
        labeler = ChurnLabeler(threshold_days=90)
        result = labeler.label_future_window(
            transactions, rfm_observed, pd.Timestamp("2011-09-09"), 90
        )
        assert result.loc[result["Customer ID"] == "C001", "CHURN"].iloc[0] == 0

    def test_no_purchase_in_window_is_churn(self, transactions, rfm_observed):
        labeler = ChurnLabeler(threshold_days=90)
        result = labeler.label_future_window(
            transactions, rfm_observed, pd.Timestamp("2011-09-09"), 90
        )
        assert result.loc[result["Customer ID"] == "C002", "CHURN"].iloc[0] == 1

    def test_purchase_on_horizon_end_counts_and_cutoff_day_does_not(self, transactions, rfm_observed):
        """Compra exactamente en corte + horizonte cuenta; compra el día del corte no."""
        labeler = ChurnLabeler(threshold_days=90)
        result = labeler.label_future_window(
            transactions, rfm_observed, pd.Timestamp("2011-09-09"), 90
        )
        # C003 compra el 2011-09-09 (corte, no cuenta) y el 2011-12-08 (borde, sí cuenta) → activo
        assert result.loc[result["Customer ID"] == "C003", "CHURN"].iloc[0] == 0

    def test_cutoff_day_purchase_alone_is_churn(self, rfm_observed):
        """Solo una compra el día del corte no evita el churn."""
        only_cutoff = pd.DataFrame({
            "Customer ID": ["C003"],
            "InvoiceDate": pd.to_datetime(["2011-09-09"]),
        })
        labeler = ChurnLabeler(threshold_days=90)
        result = labeler.label_future_window(
            only_cutoff, rfm_observed, pd.Timestamp("2011-09-09"), 90
        )
        assert result.loc[result["Customer ID"] == "C003", "CHURN"].iloc[0] == 1

    def test_label_ignores_recency(self, transactions, rfm_observed):
        """Cambiar Recency no cambia la etiqueta: solo importan las compras futuras."""
        labeler = ChurnLabeler(threshold_days=90)
        shuffled = rfm_observed.assign(Recency=[1, 1000, 1])
        a = labeler.label_future_window(transactions, rfm_observed, pd.Timestamp("2011-09-09"), 90)
        b = labeler.label_future_window(transactions, shuffled, pd.Timestamp("2011-09-09"), 90)
        assert a["CHURN"].tolist() == b["CHURN"].tolist()

    def test_report_generated(self, transactions, rfm_observed):
        labeler = ChurnLabeler(threshold_days=90)
        labeler.label_future_window(transactions, rfm_observed, pd.Timestamp("2011-09-09"), 90)
        assert labeler.report["churned"] == 1
        assert labeler.report["total_customers"] == 3

    def test_requires_customer_id(self, transactions):
        labeler = ChurnLabeler(threshold_days=90)
        with pytest.raises(ValueError, match="Customer ID"):
            labeler.label_future_window(
                transactions, pd.DataFrame({"Recency": [1]}), pd.Timestamp("2011-09-09"), 90
            )
