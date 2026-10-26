"""
src.segmentation — Capa de Segmentación de Clientes
"""
from .risk_segmenter import RiskSegmenter
from .rfm_segmenter import RFMSegmenter
from .customer_profiler import CustomerProfiler

__all__ = ["RiskSegmenter", "RFMSegmenter", "CustomerProfiler"]
