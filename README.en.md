<p align="center"><img src="https://dodysalim.github.io/assets/project-covers/churn.webp" alt="Churn Intelligence" width="100%"></p>

<h1 align="center">Churn Intelligence</h1>

<p align="center"><b>From purchase behavior to risk segments and retention scenarios.</b></p>

<p align="center"><a href="https://churnmodel2026.streamlit.app/"><b>Live demo ↗</b></a></p>

<p align="center"><img src="https://img.shields.io/badge/No_Country_·_Team_40_·_March_2026-75E6CE?style=for-the-badge&labelColor=0b1222" alt="No Country · Team 40 · March 2026"></p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="pandas"> <img src="https://img.shields.io/badge/XGBoost-1F6FEB?style=flat-square&logoColor=white" alt="XGBoost"> <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"> <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase"> <img src="https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logoColor=black" alt="Power BI">
</p>

<p align="center"><a href="https://dodysalim.github.io/"><b>🌐 Portfolio</b></a> · <a href="https://nocountry.tech/showcase/simulacion-laboral-marzo-2026/equipo-40-data-science"><b>🏆 No Country Showcase</b></a> · <a href="README.md"><b>🇪🇸 Versión en español</b></a></p>

---

## 📌 At a glance

| | |
| --- | --- |
| **🎯 Problem** | Detect e-commerce customers showing churn signals and the value at risk. |
| **🛠️ Solution** | RFM segmentation, churn labeling and XGBoost with SHAP, plus training/inference pipelines. |
| **📈 Deliverables** | 5-page Streamlit dashboard (demo mode without credentials) and Power BI. |
| **🧪 Quality** | 25 automated tests. |
| **👤 My role** | Data Analyst in a 4-person team. |

## 🏗️ Architecture

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

## 🚀 How to run

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m streamlit run Dashboard/webapp/app.py
python -m pytest tests -q
```

## ⚖️ Scope

Demo data, illustrative trends and scenario ROI are not observed results.

## 👥 Team

Team: Lucel · Junior Alexis · Geyson David · Dody (Data Analyst). Collective authorship is preserved.

---

<p align="center">
<b>Dody Dueñas Remache</b> · Data Analyst / Data Scientist · Guayaquil, Ecuador (remote LATAM)<br>
<a href="https://dodysalim.github.io/">Portfolio</a> · <a href="https://github.com/dodysalim">GitHub</a> · <a href="https://www.linkedin.com/in/dody-duenas/">LinkedIn</a> · <a href="mailto:dodydurema67@gmail.com">dodydurema67@gmail.com</a>
</p>
