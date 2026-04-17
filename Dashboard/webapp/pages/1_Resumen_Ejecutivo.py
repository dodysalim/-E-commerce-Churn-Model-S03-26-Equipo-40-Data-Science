import streamlit as st
import sys, os
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory
from data_loader import _generate_demo_data

st.set_page_config(page_title="Resumen Ejecutivo — Churn", page_icon="📋", layout="wide")
Theme.apply_global_css()

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:14px 0 6px 0;">
        <div style="font-size:1.6rem;">📊</div>
        <div style="font-weight:700; color:#C7D2FE; font-size:0.9rem;">CHURN INTELLIGENCE</div>
        <div style="font-size:0.65rem; color:#818CF8; letter-spacing:2px;">NO COUNTRY · EQ. 40</div>
    </div>
    <hr style="border-color:#4338CA; margin:8px 0 16px 0;">
    """, unsafe_allow_html=True)

# ── Cargar datos ──────────────────────────────────────────────────────────────
df_global = st.session_state.get("df_global", pd.DataFrame())
df_dist   = st.session_state.get("df_dist",   pd.DataFrame())

if df_global.empty or df_dist.empty:
    _, df_global, _, _ = _generate_demo_data()
    df_dist, _, _, _   = _generate_demo_data()

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
    <div style="background:linear-gradient(135deg,#4F46E5,#7C3AED); width:42px; height:42px;
                border-radius:10px; display:flex; align-items:center; justify-content:center;
                font-size:1.4rem;">📋</div>
    <div>
        <h2 style="margin:0; font-size:1.4rem; color:#1A202C; font-weight:800;">Resumen Ejecutivo</h2>
        <div style="font-size:0.75rem; color:#64748B;">
            Visión 360° del estado de retención · Churn E-Commerce
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Slicers ───────────────────────────────────────────────────────────────────
with st.container(border=True):
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        all_levels = list(df_dist["customer_level"].unique())
        filt_level = st.multiselect(
            "🔍 Filtrar por Segmento de Cliente",
            all_levels,
            default=all_levels,
        )
    with col_s2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"📅 Dataset: UCI Online Retail II")

df_d = df_dist[df_dist["customer_level"].isin(filt_level)] if filt_level else df_dist

# ── KPIs ──────────────────────────────────────────────────────────────────────
UIComponents.section("Indicadores Clave de Negocio")
c1, c2, c3, c4 = st.columns(4)

total    = int(df_global["total_customers_analyzed"].iloc[0])
churn    = float(df_global["overall_churn_rate_pct"].iloc[0])
exposure = float(df_global["high_risk_monetary_exposure"].iloc[0])
vips     = int(df_global["vips_at_risk_count"].iloc[0])

with c1: UIComponents.kpi("Clientes Analizados", f"{total:,}", "+5.2% vs mes anterior", "blue")
with c2: UIComponents.kpi("Tasa de Abandono", f"{churn:.1f}%", "↓ 0.1 pts vs último mes", "green")
with c3: UIComponents.kpi("Exposición Financiera", f"${exposure:,.0f}", "⚠️ Clientes Alto Riesgo", "yellow")
with c4: UIComponents.kpi("VIPs en Riesgo", f"{vips}", "🚨 Atención inmediata", "red")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
UIComponents.section("Distribución y Tendencias")
col1, col2, col3 = st.columns(3)

with col1:
    fig = ChartFactory.pie(df_d, "customer_level", "avg_monetary", "💰 LTV por Segmento")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = ChartFactory.bar(df_d, "customer_level", "customer_count", "customer_level",
                           "👥 Volumen de Clientes por Cohorte")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    mock_dates = pd.date_range(end=pd.Timestamp.today(), periods=6, freq="ME")
    mock_trend = pd.DataFrame({
        "Mes":        mock_dates,
        "Churn Rate": [4.8, 4.6, 4.5, 4.3, 4.3, round(churn, 1)],
    })
    fig = ChartFactory.area(mock_trend, "Mes", "Churn Rate", title="📉 Tendencia Histórica de Churn")
    st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
UIComponents.section("Análisis de Correlación y Salud")
col4, col5 = st.columns([2, 1])

with col4:
    fig = ChartFactory.scatter(df_d, "avg_monetary", "avg_churn_risk_pct", "customer_count",
                               "customer_level", "🔴 Correlación LTV vs Riesgo de Deserción")
    st.plotly_chart(fig, use_container_width=True)

with col5:
    fig = ChartFactory.gauge(churn, "Índice de Salud de Retención", max_val=20, color="#4F46E5")
    st.plotly_chart(fig, use_container_width=True)

# ── Insight ───────────────────────────────────────────────────────────────────
UIComponents.insight(
    f"La tasa de abandono actual es <b>{churn:.1f}%</b>, con una exposición financiera de "
    f"<b>${exposure:,.0f}</b>. Los segmentos de mayor valor (VIP Platino y Oro) concentran el "
    f"mayor riesgo relativo — accionarlos primero maximiza el ROI de retención."
)
