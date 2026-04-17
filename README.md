# 📊 E-Commerce Churn Prediction Pipeline

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-red)](https://xgboost.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?logo=supabase)](https://supabase.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange?logo=scikit-learn)](https://scikit-learn.org)
[![AUC-ROC](https://img.shields.io/badge/AUC--ROC-0.912-brightgreen)](reports/)
[![License](https://img.shields.io/badge/Licencia-No%20Country-purple)](https://nocountry.tech)

> **Proyecto:** No Country — Equipo 40 | Sprint 3
> **Dataset:** Online Retail II (UCI ML Repository) — ~1M transacciones
> **Objetivo:** Predecir y prevenir el abandono de clientes en E-Commerce con ML interpretable

---

## 🎯 Resultados Clave del Modelo

| Métrica | Valor | Descripción |
|---------|-------|-------------|
| **AUC-ROC** | **0.912** | Supera benchmark de industria (0.85) |
| **Precision** | **87.4%** | Clase Alto Riesgo |
| **Recall** | **83.1%** | Churners correctamente detectados |
| **F1-Score** | **85.2%** | Balance Precision / Recall |
| **Modelo Champion** | XGBoost | Seleccionado por validación cruzada 5-Fold |
| **Feature #1 (SHAP)** | Recency | Peso 0.38 — clientes inactivos 60+ días tienen 3.4× más riesgo |

---

## 🚀 Dashboard — Loyalty & Retention Intelligence

El proyecto incluye un **dashboard Streamlit Enterprise** con 5 módulos analíticos en tiempo real.

### Levantar el Dashboard

```bash
cd Dashboard/webapp
pip install -r ../../requirements.txt
streamlit run app.py
```

Disponible en: `http://localhost:8501`

> **Modo Demo:** Si Supabase no está disponible, el dashboard activa automáticamente datos simulados realistas (800+ clientes) sin necesidad de conexión.

### Módulos del Dashboard

| # | Módulo | Descripción |
|---|--------|-------------|
| 01 | **Resumen Ejecutivo** | KPIs globales, tasa de churn, exposición financiera, tendencia histórica |
| 02 | **Predicciones ML** | Probabilidades individuales, Feature Importance SHAP, distribución de riesgo |
| 03 | **Valor & Riesgo** | Treemap de zonas de peligro, cascada de exposición LTV, radar de severidad |
| 04 | **Segmentación RFM** | Cubo 3D interactivo Recency×Frequency×Monetary, clustering espacial |
| 05 | **Plan de Acción VIP** | Estrategias auto-asignadas por ROI, matriz maestra de intervención comercial |

---

## 🏗️ Arquitectura Enterprise

```
proyectodechurndenocountry/
├── 📁 Dashboard/                 # 🚀 WebApp Streamlit Enterprise
│   └── webapp/
│       ├── app.py                # Punto de entrada — portada y precarga de datos
│       ├── data_loader.py        # Repositorio Supabase + modo demo offline
│       ├── components.py         # Theme, UIComponents, ChartFactory
│       └── pages/
│           ├── 1_Resumen_Ejecutivo.py
│           ├── 2_Predicciones_ML.py
│           ├── 3_Valor_Riesgo.py
│           ├── 4_RFM_Segmentacion.py
│           └── 5_Plan_Accion.py
│
├── 📁 config/                    # Configuración centralizada (YAML)
│   ├── config.yaml               # Hiperparámetros, umbrales, rutas
│   └── logging_config.yaml       # Logging estructurado rotativo
│
├── 📁 data/
│   ├── raw/                      # Dataset original (INMUTABLE)
│   ├── interim/                  # Datos limpios (Parquet)
│   ├── processed/                # RFM + splits de train/test
│   └── exports/                  # CSVs listos para BI
│
├── 📁 docs/                      # Documentación técnica y de negocio
│   ├── data_dictionary.md
│   ├── powerbi_setup_guide.md
│   └── model_card.md
│
├── 📁 models/
│   ├── registry/v1.0/            # Artefactos + metadata por versión
│   └── champion/                 # Modelo activo en producción
│
├── 📁 notebooks/                 # Análisis exploratorio y experimentación
│   ├── 01_eda.ipynb
│   ├── 02_churn_definition.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modeling_experiments.ipynb
│   ├── 05_shap_interpretability.ipynb
│   ├── 06_segmentation_analysis.ipynb
│   └── 07_executive_summary.ipynb
│
├── 📁 pipelines/                 # Orquestadores por caso de uso
│   ├── run_full_pipeline.py      # ← Punto de entrada principal
│   ├── run_training_pipeline.py
│   ├── run_inference_pipeline.py
│   └── run_export_pipeline.py
│
├── 📁 src/                       # Código fuente — arquitectura por dominios
│   ├── data/          → loader, validator, versioner
│   ├── features/      → preprocessing, rfm_builder, advanced_features, scaler
│   ├── labeling/      → churn_label, threshold_analyzer
│   ├── modeling/      → trainer, evaluator, interpreter, registry
│   ├── segmentation/  → risk_segmenter, rfm_segmenter, customer_profiler
│   └── export/        → supabase_connector, csv_exporter, schema_deployer
│
├── 📁 sql/
│   ├── migrations/               # Control de versiones del schema
│   ├── views.sql                 # 6 vistas analíticas
│   └── policies.sql              # Row Level Security (RLS)
│
├── 📁 reports/
│   ├── executive_dashboard.png   # Captura del dashboard en producción
│   └── figures/
│       ├── eda/                  # Distribuciones RFM, análisis temporal
│       ├── modeling/             # Curvas ROC, matriz de confusión
│       └── shap/                 # Feature importance, summary plots
│
├── 📁 tests/
│   ├── unit/
│   └── integration/
│
├── 📁 monitoring/
│   └── drift_detector.py         # KS Test + Evidently AI
│
├── Makefile
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

---

## ⚡ Inicio Rápido

### 1. Instalación

```bash
cd proyectodechurndenocountry
make install-dev
make create-dirs
```

### 2. Variables de Entorno

```bash
cp ../.env.example ../.env
# Editar con tus credenciales Supabase:
# SUPABASE_URL=https://[project-ref].supabase.co
# SUPABASE_KEY=tu_anon_key
# SUPABASE_DB_URL=postgresql://postgres:[pass]@db.[ref].supabase.co:5432/postgres
```

### 3. Desplegar Schema en Supabase

```bash
make db-deploy
```

### 4. Ejecutar el Pipeline Completo

```bash
make run
# O directamente:
python pipelines/run_full_pipeline.py
```

### 5. Levantar el Dashboard

```bash
cd Dashboard/webapp
streamlit run app.py
# → http://localhost:8501
```

---

## 🤖 Comandos Disponibles (Makefile)

```bash
make run           # Pipeline completo (carga → entrenamiento → exportación)
make train         # Solo entrenamiento
make infer         # Inferencia sobre nuevos datos
make export        # Solo exportación a Supabase/CSV
make test          # Suite completa de tests
make test-unit     # Solo tests unitarios (rápidos)
make format        # Formatear código (black + isort)
make lint          # Verificar estilo (flake8)
make status        # Estado actual del pipeline
make clean         # Limpiar cachés Python
```

---

## 🧪 Metodología

| Etapa | Detalle |
|-------|---------|
| **Criterio de Churn** | 90 días de inactividad comercial (validado con `ThresholdAnalyzer`) |
| **Features Base** | Recency, Frequency, Monetary (RFM) |
| **Features Avanzadas** | AvgTicket, DaysBetweenPurchases, MonetaryStdDev, UniqueProducts, PeakHourBuyer |
| **Desbalance de Clases** | SMOTE + `scale_pos_weight` dinámico (XGBoost) |
| **Selección de Modelo** | Validación cruzada estratificada 5-Fold — 5 algoritmos comparados |
| **Interpretabilidad** | SHAP TreeExplainer — summary, bar y dependence plots |
| **Segmentación** | Alto / Medio / Bajo Riesgo con probabilidad individual 0-100% |
| **Versionado de Modelos** | Registry local con metadata JSON + champion activo |
| **Monitoreo de Drift** | Kolmogorov-Smirnov test + Evidently AI |

---

## 💰 Impacto de Negocio

| Métrica | Valor |
|---------|-------|
| Exposición financiera detectada | **$387,420** |
| Inversión requerida (5% del LTV) | Estimado conservador |
| ROI proyectado a 90 días | **18%** |
| Multiplicador ROI | **3.6×** |
| Reducción de churn alcanzable | **35%** con plan de acción |

### Estrategias de Retención Auto-asignadas

| Canal | Audiencia | Impacto |
|-------|-----------|---------|
| 📞 Llamada Ejecutiva | Top 10% riesgo (score ≥ 90%) | 52% del valor recuperado |
| 📧 Email + Descuento | Riesgo medio (score 70-90%) | 31% del valor recuperado |
| 🤝 Seguimiento CSM | Riesgo bajo (score < 70%) | 17% del valor recuperado |

---

## 📈 Stack Tecnológico

| Categoría | Tecnologías |
|-----------|-------------|
| **ML** | scikit-learn 1.4, XGBoost 2.0, imbalanced-learn |
| **Interpretabilidad** | SHAP 0.45 |
| **Datos** | pandas 2.2, numpy 1.26, pyarrow (Parquet) |
| **Dashboard** | Streamlit, Plotly |
| **Base de Datos** | Supabase (PostgreSQL), supabase-py 2.x |
| **Testing** | pytest + pytest-cov |
| **Calidad** | black, isort, flake8, pre-commit |
| **Monitoreo** | Evidently AI, scipy |

---

## 📄 Licencia

Este proyecto es parte de la iniciativa **No Country** — Sprint 3, Equipo 40.
Desarrollado con fines educativos y de portafolio profesional.
