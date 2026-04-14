# 📊 E-Commerce Churn Prediction Pipeline

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange?logo=scikit-learn)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-red)](https://xgboost.readthedocs.io)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?logo=supabase)](https://supabase.com)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow?logo=powerbi)](https://powerbi.microsoft.com)

> **Proyecto:** No Country — Equipo 40 | Sprint 3  
> **Dataset:** Online Retail II (UCI ML Repository) — ~1M transacciones  
> **Objetivo:** Predecir y prevenir el abandono de clientes en E-Commerce

---

## 🏗️ Arquitectura Enterprise

```
proyectodechurndenocountry/
├── 📁 Dashboard/                 # 🚀 WebApp Streamlit Enterprise
│   └── webapp/                   # Interfaz de Inteligencia de Negocio
│       ├── app.py                # Punto de entrada / Portada
│       ├── data_loader.py        # Repositorio Supabase
│       ├── components.py         # UI y Motor CSS
│       └── pages/                # Vistas Analíticas
│
├── 📁 config/                    # Configuración centralizada (YAML)
│   ├── config.yaml               # Hiperparámetros, umbrales, rutas
│   └── logging_config.yaml       # Logging estructurado rotativo
│
├── 📁 data/
│   ├── raw/                      # Dataset original (INMUTABLE)
│   ├── interim/                  # Datos limpios (Parquet)
│   ├── processed/                # RFM + splits de train/test
│   └── exports/                  # CSVs listos para Power BI
│
├── 📁 docs/                      # Documentación técnica y de negocio
│   ├── data_dictionary.md        # Descripción de cada columna
│   ├── powerbi_setup_guide.md    # Guía de conexión Power BI ↔ Supabase
│   └── model_card.md             # Sesgo, limitaciones y contexto del modelo
│
├── 📁 models/
│   ├── registry/v1.0/            # Artefactos + metadata por versión
│   └── champion/                 # Modelo activo en producción
│
├── 📁 notebooks/                 # Análisis exploratorio y experimentación
│   ├── 01_eda.ipynb              # EDA completo del dataset
│   ├── 02_churn_definition.ipynb # Análisis del umbral de inactividad
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modeling_experiments.ipynb
│   ├── 05_shap_interpretability.ipynb
│   ├── 06_segmentation_analysis.ipynb
│   └── 07_executive_summary.ipynb
│
├── 📁 pipelines/                 # Orquestadores por caso de uso
│   ├── run_full_pipeline.py      # ← Punto de entrada principal
│   ├── run_training_pipeline.py  # Solo entrenamiento
│   ├── run_inference_pipeline.py # Predicción sobre nuevos datos
│   └── run_export_pipeline.py    # Solo exportación
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
│   ├── views.sql                 # 6 vistas para Power BI
│   └── policies.sql              # Row Level Security (RLS)
│
├── 📁 tests/                     # Suite de pruebas
│   ├── unit/                     # Tests rápidos por módulo
│   └── integration/              # Tests del pipeline completo
│
├── 📁 monitoring/                # Monitoreo en producción
│   └── drift_detector.py         # KS Test + Evidently AI
│
├── Makefile                      # Comandos de automatización
├── pyproject.toml                # Configuración del proyecto
├── requirements.txt              # Dependencias de producción
└── requirements-dev.txt          # Dependencias de desarrollo
```

---

## ⚡ Inicio Rápido

### 1. Instalación

```bash
# Clonar y entrar al proyecto
cd proyectodechurndenocountry

# Instalar dependencias
make install-dev

# Crear estructura de directorios
make create-dirs
```

### 2. Configurar Variables de Entorno

```bash
# Copiar el template
cp ../.env.example ../.env

# Editar con tus credenciales
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
# Pipeline end-to-end (carga → entrenamiento → exportación)
make run

# O directamente:
python pipelines/run_full_pipeline.py
```

### 5. Ver Resultados

- **📁 CSV:** `data/exports/`
- **☁️ Supabase:** Dashboard en Supabase Studio
- **📊 Power BI:** Seguir `docs/powerbi_setup_guide.md`
- **📋 Métricas:** `reports/metrics.md`
- **💡 Insights:** `reports/insights.md`

---

## 🤖 Comandos Disponibles (Makefile)

```bash
make run           # Pipeline completo
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
| **Desbalance de Clases** | `class_weight='balanced'` (RF, LR) + `scale_pos_weight` dinámico (XGBoost) |
| **Selección de Modelo** | Validación cruzada estratificada 5-Fold, priorizando **Recall** |
| **Interpretabilidad** | SHAP TreeExplainer — summary, bar, dependence plots |
| **Versionado de Modelos** | Registry local con metadata JSON + champion activo |
| **Monitoreo de Drift** | Kolmogorov-Smirnov test + Evidently AI |

---

## 📈 Stack Tecnológico

| Categoría | Tecnologías |
|-----------|------------|
| ML | scikit-learn 1.4, XGBoost 2.0, imbalanced-learn |
| Interpretabilidad | SHAP 0.45 |
| Datos | pandas 2.2, numpy 1.26, pyarrow (Parquet) |
| Base de Datos | Supabase (PostgreSQL), supabase-py 2.x |
| Visualización | matplotlib, seaborn, plotly |
| Testing | pytest + pytest-cov |
| Calidad | black, isort, flake8, pre-commit |
| Monitoreo | Evidently AI, scipy |
| Contenedor | Docker |

---

## 📄 Licencia

Este proyecto es parte de la iniciativa **No Country** — Sprint 3, Equipo 40.  
Desarrollado con fines educativos y de portafolio profesional.