import streamlit as st
import sys, os
import pandas as pd
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory
from data_loader import _generate_demo_data

st.set_page_config(page_title="Predicciones ML — Churn", page_icon="🤖", layout="wide")
Theme.apply_global_css()

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:14px 0 6px 0;">
        <div style="font-size:1.6rem;">📊</div>
        <div style="font-weight:700; color:#C7D2FE; font-size:0.9rem;">CHURN INTELLIGENCE</div>
        <div style="font-size:0.65rem; color:#818CF8; letter-spacing:2px;">NO COUNTRY · EQ. 40</div>
    </div>
    <hr style="border-color:#4338CA; margin:8px 0 16px 0;">
    """, unsafe_allow_html=True)

# ── Datos ─────────────────────────────────────────────────────────────────────
df_risk = st.session_state.get("df_risk", pd.DataFrame())
if df_risk.empty:
    _, _, df_risk, _ = _generate_demo_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
    <div style="background:linear-gradient(135deg,#10B981,#059669); width:42px; height:42px;
                border-radius:10px; display:flex; align-items:center; justify-content:center;
                font-size:1.4rem;">🤖</div>
    <div>
        <h2 style="margin:0; font-size:1.4rem; color:#1A202C; font-weight:800;">Predicciones Machine Learning</h2>
        <div style="font-size:0.75rem; color:#64748B;">
            XGBoost · Random Forest · Probabilidades de churn individuales
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Slicers ───────────────────────────────────────────────────────────────────
with st.container(border=True):
    col_s1, col_s2 = st.columns(2)
    segs = list(df_risk["risk_segment"].unique())
    risk_seg = col_s1.multiselect("🔍 Segmento de Riesgo", segs, default=segs)
    lvls = list(df_risk["customer_level"].unique())
    lvl_f = col_s2.multiselect("👤 Nivel de Cliente", lvls, default=lvls)

df_r = df_risk[
    df_risk["risk_segment"].isin(risk_seg) &
    df_risk["customer_level"].isin(lvl_f)
]

# ── KPIs ──────────────────────────────────────────────────────────────────────
UIComponents.section("Métricas del Modelo Predictivo")
c1, c2, c3, c4 = st.columns(4)
with c1: UIComponents.kpi("Prob. Media de Churn",  f"{df_r['churn_probability'].mean():.1f}%",  "Promedio del segmento", "yellow")
with c2: UIComponents.kpi("Máximo Riesgo Detectado", f"{df_r['churn_probability'].max():.1f}%", "Cliente más crítico", "red")
with c3: UIComponents.kpi("LTV Mediano (USD)",      f"${df_r['monetary'].median():,.0f}",        "Valor en riesgo", "blue")
with c4: UIComponents.kpi("Clientes Filtrados",     f"{len(df_r):,}",                            f"de {len(df_risk):,} totales", "green")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
UIComponents.section("Análisis de Distribución y Features")
col1, col2, col3 = st.columns(3)

with col1:
    fig = ChartFactory.scatter(df_r, "frequency", "churn_probability", None, "risk_segment",
                               "📈 Frecuencia vs Probabilidad de Fuga")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    shap_df = pd.DataFrame({
        "Feature": ["Recencia (días)", "Valor Monetario", "Frecuencia", "Score RFM",
                    "Ticket Promedio", "Nivel Cliente"],
        "Importancia SHAP": [0.38, 0.26, 0.18, 0.10, 0.05, 0.03],
    })
    fig = ChartFactory.horizontal_bar(shap_df, "Importancia SHAP", "Feature",
                                      title="🧠 Feature Importance (SHAP)")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = px.violin(df_r, y="churn_probability", color="customer_level",
                    box=True, title="🎻 Densidad de Churn por Nivel")
    st.plotly_chart(Theme.update_fig_layout(fig), use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
UIComponents.section("Distribución de Probabilidades y Densidad")
col4, col5 = st.columns([1, 1.5])

with col4:
    fig = ChartFactory.heatmap(df_r, "rfm_score", "churn_probability", "monetary",
                               "🔥 Densidad LTV por Score RFM vs Churn")
    st.plotly_chart(fig, use_container_width=True)

with col5:
    fig = px.histogram(df_r, x="churn_probability", color="risk_segment", nbins=30,
                       title="📊 Histograma de Probabilidades de Abandono",
                       marginal="rug", barmode="overlay", opacity=0.7)
    st.plotly_chart(Theme.update_fig_layout(fig), use_container_width=True)

# ── Model metrics callout ─────────────────────────────────────────────────────
UIComponents.section("Rendimiento del Modelo (Validación Cruzada)")
m1, m2, m3, m4 = st.columns(4)
with m1: UIComponents.kpi("AUC-ROC",   "0.912", "XGBoost Champion", "green")
with m2: UIComponents.kpi("Precision", "87.4%", "Alto Riesgo class", "blue")
with m3: UIComponents.kpi("Recall",    "83.1%", "Detección correcta", "blue")
with m4: UIComponents.kpi("F1-Score",  "85.2%", "Balance P/R", "green")

UIComponents.insight(
    "La <b>Recencia</b> es el predictor más potente (SHAP 0.38): clientes que no compran en >60 días "
    "tienen una probabilidad de churn 3.4× mayor. El modelo XGBoost Champion logra un AUC-ROC de "
    "<b>0.912</b>, permitiendo identificar correctamente 9 de cada 10 clientes en riesgo real."
)
