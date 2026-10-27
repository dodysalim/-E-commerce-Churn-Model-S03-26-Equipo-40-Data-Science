<p align="center"><img src="https://dodysalim.github.io/assets/project-covers/churn.webp" alt="Churn Intelligence" width="100%"></p>

<h1 align="center">Churn Intelligence</h1>

<p align="center"><b>Del comportamiento de compra a segmentos de riesgo y escenarios de retención.</b></p>

<p align="center">
<img src="https://img.shields.io/badge/No_Country_%C2%B7_Equipo_40_%C2%B7_Marzo_2026-75E6CE?style=for-the-badge&labelColor=0b1222" alt="No Country · Equipo 40 · Marzo 2026">
</p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="pandas"> <img src="https://img.shields.io/badge/XGBoost-1F6FEB?style=flat-square&logoColor=white" alt="XGBoost"> <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"> <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase"> <img src="https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logoColor=black" alt="Power BI">
</p>

<p align="center">
<a href="https://github.com/dodysalim/-E-commerce-Churn-Model-S03-26-Equipo-40-Data-Science/actions"><img src="https://github.com/dodysalim/-E-commerce-Churn-Model-S03-26-Equipo-40-Data-Science/actions/workflows/ci_pipeline.yml/badge.svg" alt="CI"></a> <img src="https://img.shields.io/badge/versión-1.1.0-8F7BFF?style=flat-square" alt="Versión 1.1.0">
</p>

<p align="center"><a href="https://nocountry.tech/showcase/simulacion-laboral-marzo-2026/equipo-40-data-science"><b>🏆 Showcase No Country</b></a> · <a href="https://dodysalim.github.io/"><b>🌐 Portafolio</b></a> · <a href="docs/PORTFOLIO_CASE.md"><b>📄 Caso de estudio</b></a> · <a href="README.en.md"><b>🇺🇸 English</b></a></p>

---

## 📌 Resumen en 30 segundos

| | |
| --- | --- |
| **🎯 Problema** | Detectar clientes de e-commerce con señales de abandono y el valor que está en riesgo. |
| **🛠️ Solución** | Segmentación RFM, etiquetado de churn y modelo XGBoost, con pipelines de entrenamiento e inferencia. |
| **📈 Entregables** | Dashboard Streamlit de 5 vistas (modo demo sin credenciales) y Power BI para PC y móvil. |
| **🧪 Calidad** | 25 pruebas automatizadas aprobadas. |
| **👤 Mi rol** | Data Analyst en equipo multidisciplinario de 4 personas. |

## ❓ La pregunta de negocio

¿Qué clientes muestran señales de abandono y qué segmentos concentran el valor expuesto?

## ✨ Qué incluye

- Preprocesamiento de transacciones, RFM y etiquetado de churn.
- Pipelines de entrenamiento, evaluación y exportación.
- Dashboard de cinco vistas, con demostración sintética identificada.

## 🏗️ Arquitectura

```mermaid
flowchart LR
    RAW[(Online Retail II)] --> DATA[data<br/>loader · validator]
    DATA --> PRE[preprocessing] --> LAB[churn_label]
    LAB --> FE[features<br/>RFM] --> MOD[modeling<br/>XGBoost + SHAP]
    FE --> SEG[segmentation]
    MOD --> EXP[export]
    SEG --> EXP
    EXP --> SB[(Supabase)]
    SB --> UI[Dashboard Streamlit<br/>5 páginas]
    DEMO[Modo demo<br/>800 clientes sintéticos] -.-> UI
    SB --> PBI[Power BI]
```

## 🚀 Cómo ejecutarlo

Usa Python 3.11 o 3.12 en un entorno independiente. Desde la raíz:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Después de configurar los datos:

```bash
python -m streamlit run Dashboard/webapp/app.py
```

## ☁️ Publicar el dashboard gratis

[![Deploy en Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=dodysalim/-E-commerce-Churn-Model-S03-26-Equipo-40-Data-Science&branch=main&mainModule=Dashboard/webapp/app.py)

Un clic abre Streamlit Community Cloud con este repositorio y `Dashboard/webapp/app.py` preconfigurados (dependencias: `requirements.txt`). Funciona sin credenciales: modo demo con 800 clientes sintéticos.

## 🗂️ Datos y configuración

La demostración funciona sin Supabase con 800 clientes sintéticos. Para usar las vistas reales, configura SUPABASE_URL y SUPABASE_KEY (anon, solo lectura con RLS) para el dashboard, y SUPABASE_SERVICE_KEY (secreta) para el pipeline que escribe. Los importes conservan las unidades de origen.

## 📊 Power BI · PC y móvil

[Archivos e instrucciones](powerbi/README.md). Descarga el repositorio completo y abre `powerbi/Abrir-PowerBI.bat` en Windows; después pulsa **Actualizar**. Incluye A4 horizontal a tamaño real (100 %) y diseño móvil vertical. El archivo `.pbip` necesita sus carpetas Report, SemanticModel y data.

## 🧭 Estructura del repositorio

| Ruta | Qué contiene |
| --- | --- |
| [src/](src/) | Limpieza, características, modelos y segmentación |
| [pipelines/](pipelines/) | Entrenamiento, inferencia y exportación |
| [Dashboard/webapp/](Dashboard/webapp/) | Interfaz Streamlit |
| [sql/](sql/) | Esquema y vistas de Supabase |
| [tests/](tests/) | Pruebas unitarias |

## ✅ Calidad y alcance

25 pruebas aprobadas, incluidas cinco regresiones de datos del dashboard. Inicio y las cinco páginas de análisis probados en modo demo sin excepciones (26-10-2026).

Los datos demo, tendencias ilustrativas y ROI de escenarios no son resultados observados. No se repitió el entrenamiento sobre Online Retail II ni se comprobó Supabase en vivo.

Para repetir las pruebas desde la raíz:

```bash
python -m pytest tests -q
```

## 👥 Autoría

Simulación No Country, Sprint 3, Equipo 40. Se mantiene la atribución colectiva y la documentación original.


### Equipo · Marzo 2026

| Integrante | Rol publicado |
| --- | --- |
| Lucel | Data |
| Junior Alexis | Data Scientist |
| Geyson David | Data Scientist |
| Dody | Data analyst |

Créditos basados en el [showcase oficial](https://nocountry.tech/showcase/simulacion-laboral-marzo-2026/equipo-40-data-science). Se conserva la autoría colectiva.

[Documentación anterior](docs/ORIGINAL_README.md), conservada como referencia histórica.

---

<p align="center">
<b>Dody Dueñas Remache</b> · Analista de Datos / Data Scientist<br>
<a href="https://dodysalim.github.io/">Portafolio</a> · <a href="https://github.com/dodysalim">GitHub</a> · <a href="https://www.linkedin.com/in/dody-duenas/">LinkedIn</a> · <a href="mailto:dodydurema67@gmail.com">dodydurema67@gmail.com</a>
</p>
