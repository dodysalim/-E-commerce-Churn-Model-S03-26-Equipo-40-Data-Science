"""
E-Commerce Churn Prediction — Paquete Raíz
==========================================
Pipeline modular enterprise para predicción de abandono de clientes.

Subdominios:
  - src.data        → Carga, validación y trazabilidad del dataset
  - src.features    → Ingeniería de características (RFM + avanzadas)
  - src.labeling    → Definición y análisis del criterio de Churn
  - src.modeling    → Entrenamiento, evaluación, optimización e interpretabilidad
  - src.segmentation → Perfilado y segmentación de clientes
  - src.export      → Conectores de salida (Supabase, CSV)
"""

__version__ = "2.0.0"
__author__ = "No Country - Equipo 40"
