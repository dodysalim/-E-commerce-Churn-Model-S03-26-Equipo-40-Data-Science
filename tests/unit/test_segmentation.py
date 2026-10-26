"""
tests/unit/test_segmentation.py — Tests de Segmentadores
"""
import pandas as pd
import pytest

from src.segmentation.rfm_segmenter import RFMSegmenter


@pytest.mark.unit
class TestRFMSegmenter:
    """Tests unitarios para RFMSegmenter."""

    def test_scores_created(self, sample_rfm):
        """R_Score, F_Score, M_Score y RFM_Score deben existir."""
        segmenter = RFMSegmenter()
        result = segmenter.transform(sample_rfm)
        for col in ["R_Score", "F_Score", "M_Score", "RFM_Score", "CustomerLevel"]:
            assert col in result.columns, f"Falta la columna: {col}"

    def test_scores_in_valid_range(self, sample_rfm):
        """Los scores R, F, M deben estar entre 1 y 4."""
        segmenter = RFMSegmenter()
        result = segmenter.transform(sample_rfm)
        for col in ["R_Score", "F_Score", "M_Score"]:
            assert result[col].between(1, 4).all(), f"{col} fuera de rango [1, 4]"

    def test_rfm_score_is_sum(self, sample_rfm):
        """RFM_Score debe ser la suma de R+F+M."""
        segmenter = RFMSegmenter()
        result = segmenter.transform(sample_rfm)
        expected_sum = result["R_Score"] + result["F_Score"] + result["M_Score"]
        assert (result["RFM_Score"] == expected_sum).all()

    def test_customer_level_valid_values(self, sample_rfm):
        """CustomerLevel solo puede tener los valores definidos."""
        valid_levels = {"VIP / Champion", "Leales / Prometedores", "En Riesgo / Perdidos"}
        segmenter = RFMSegmenter()
        result = segmenter.transform(sample_rfm)
        assert set(result["CustomerLevel"].unique()).issubset(valid_levels)

    def test_raises_without_required_columns(self):
        """Debe lanzar ValueError si faltan columnas requeridas."""
        df = pd.DataFrame({"Customer ID": ["C001"]})
        segmenter = RFMSegmenter()
        with pytest.raises(ValueError, match="faltantes"):
            segmenter.transform(df)

    def test_no_mutation_of_input(self, sample_rfm):
        """El DataFrame original no debe ser modificado."""
        original_cols = set(sample_rfm.columns)
        segmenter = RFMSegmenter()
        segmenter.transform(sample_rfm)
        assert set(sample_rfm.columns) == original_cols
