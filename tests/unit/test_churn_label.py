"""
tests/unit/test_churn_label.py — Tests del ChurnLabeler
"""
import pandas as pd
import pytest

from src.labeling.churn_label import ChurnLabeler


@pytest.mark.unit
class TestChurnLabeler:
    """Tests unitarios para ChurnLabeler."""

    def test_churn_label_created(self, sample_rfm):
        """La columna CHURN debe existir tras el transform."""
        labeler = ChurnLabeler(threshold_days=90)
        result = labeler.transform(sample_rfm)
        assert "CHURN" in result.columns

    def test_churn_values_binary(self, sample_rfm):
        """CHURN solo puede ser 0 o 1."""
        labeler = ChurnLabeler(threshold_days=90)
        result = labeler.transform(sample_rfm)
        assert set(result["CHURN"].unique()).issubset({0, 1})

    def test_recency_above_threshold_is_churn(self):
        """Clientes con Recency > threshold → CHURN = 1."""
        df = pd.DataFrame({
            "Customer ID": ["C001", "C002"],
            "Recency": [91, 30],
            "Frequency": [5, 10],
            "Monetary": [100.0, 500.0],
        })
        labeler = ChurnLabeler(threshold_days=90)
        result = labeler.transform(df)
        assert result.loc[result["Customer ID"] == "C001", "CHURN"].iloc[0] == 1
        assert result.loc[result["Customer ID"] == "C002", "CHURN"].iloc[0] == 0

    def test_raises_without_recency_column(self):
        """Debe lanzar ValueError si falta la columna Recency."""
        df = pd.DataFrame({"Customer ID": ["C001"], "Frequency": [5]})
        labeler = ChurnLabeler()
        with pytest.raises(ValueError, match="Recency"):
            labeler.transform(df)

    def test_report_generated(self, sample_rfm):
        """El reporte de balance de clases debe generarse."""
        labeler = ChurnLabeler(threshold_days=90)
        labeler.transform(sample_rfm)
        report = labeler.report
        assert report is not None
        assert "churn_rate_pct" in report
        assert 0 <= report["churn_rate_pct"] <= 100

    def test_different_thresholds_produce_different_rates(self, sample_rfm):
        """Umbrales distintos deben producir tasas de churn distintas."""
        labeler_30 = ChurnLabeler(threshold_days=30)
        labeler_180 = ChurnLabeler(threshold_days=180)
        r30 = labeler_30.transform(sample_rfm)
        r180 = labeler_180.transform(sample_rfm)
        rate30 = r30["CHURN"].mean()
        rate180 = r180["CHURN"].mean()
        # Con threshold mayor, menos clientes se clasifican como churn
        assert rate30 >= rate180

    def test_no_mutation_of_input(self, sample_rfm):
        """El DataFrame original no debe ser modificado."""
        original_columns = list(sample_rfm.columns)
        labeler = ChurnLabeler()
        labeler.transform(sample_rfm)
        assert list(sample_rfm.columns) == original_columns
