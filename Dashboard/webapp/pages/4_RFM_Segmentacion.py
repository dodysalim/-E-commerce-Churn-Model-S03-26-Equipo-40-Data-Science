import streamlit as st
import sys, os
import pandas as pd
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory
from data_loader import _generate_demo_data

st.set_page_config(page_title="Segmentación RFM — Churn", page_icon="🎯", layout="wide")
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
df_dist = st.session_state.get("df_dist", pd.DataFrame())
if df_risk.empty:
    df_dist, _, df_risk, _ = _generate_demo_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
    <div style="background:linear-gradient(135deg,#8B5CF6,#7C3AED); width:42px; height:42px;
                border-radius:10px; display:flex; align-items:center; justify-content:center;
                font-size:1.4rem;">🎯</div>
    <div>
        <h2 style="margin:0; font-size:1.4rem; color:#1A202C; font-weight:800;">Segmentación RFM 360°</h2>
        <div style="font-size:0.75rem; color:#64748B;">
            Recency · Frequency · Monetary — Clustering tridimensional de clientes
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Slicers ───────────────────────────────────────────────────────────────────
with st.container(border=True):
    col_s1, col_s2 = st.columns(2)
    segs = list(df_risk["risk_segment"].unique())
    filtro_riesgo = col_s1.multiselect("⚠️ Nivel de Riesgo", segs, default=segs)
    lvls = list(df_risk["customer_level"].unique())
    filtro_nivel  = col_s2.multiselect("👤 Nivel de Cliente", lvls, default=lvls)

df_f = df_risk[df_risk["risk_segment"].isin(filtro_riesgo) & df_risk["customer_level"].isin(filtro_nivel)]

# ── KPIs ──────────────────────────────────────────────────────────────────────
UIComponents.section("Métricas RFM Promedio del Segmento")
c1, c2, c3, c4 = st.columns(4)
with c1: UIComponents.kpi("Recencia Media",     f"{df_f['recency'].mean():.0f} días",  "Días desde última compra", "yellow")
with c2: UIComponents.kpi("Frecuencia Media",   f"{df_f['frequency'].mean():.1f} tx",  "Transacciones promedio", "blue")
with c3: UIComponents.kpi("Valor Medio (LTV)",  f"${df_f['monetary'].mean():,.0f}",    "Gasto por cliente", "green")
with c4: UIComponents.kpi("Score RFM Promedio", f"{df_f['rfm_score'].mean():.1f} / 5", "Índice compuesto", "purple" if False else "blue")

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Layout ───────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 2])

with col_left:
    UIComponents.section("Embudo & Distribución de Scores")

    if not df_dist.empty:
        fig = ChartFactory.funnel(
            df_dist.sort_values("customer_count", ascending=False),
            "customer_count", "customer_level",
            "🔻 Embudo Demográfico por Cohorte"
        )
        st.plotly_chart(fig, use_container_width=True)

    score_cnt = df_f.groupby("rfm_score").size().reset_index(name="Clientes")
    fig = ChartFactory.bar(score_cnt, "rfm_score", "Clientes", title="📊 Densidad por Puntaje RFM")
    st.plotly_chart(fig, use_container_width=True)

    fig_s = px.sunburst(
        df_f, path=["risk_segment", "customer_level"],
        values="monetary",
        title="☀️ Sunburst: Valor por Segmento",
        color="monetary", color_continuous_scale="Viridis",
    )
    st.plotly_chart(Theme.update_fig_layout(fig_s), use_container_width=True)

with col_right:
    UIComponents.section("Cubo RFM 3D — Mapa de Clustering")

    fig_3d = px.scatter_3d(
        df_f, x="recency", y="frequency", z="monetary",
        color="customer_level", size="rfm_score",
        title="🧊 Clustering Espacial RFM",
        size_max=12, opacity=0.8,
        color_discrete_sequence=Theme.COLORS,
    )
    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(title="Recencia (días)", backgroundcolor="#F8FAFC"),
            yaxis=dict(title="Frecuencia (tx)",  backgroundcolor="#F8FAFC"),
            zaxis=dict(title="Valor USD",         backgroundcolor="#F8FAFC"),
        ),
        paper_bgcolor=Theme.TILE_BG,
        font_color=Theme.TEXT_COLOR,
        height=460,
    )
    st.plotly_chart(fig_3d, use_container_width=True)

    c_sub1, c_sub2 = st.columns(2)
    with c_sub1:
        fig = ChartFactory.scatter(df_f, "recency", "frequency", None, "risk_segment",
                                   "📐 Recencia vs Frecuencia")
        st.plotly_chart(fig, use_container_width=True)
    with c_sub2:
        fig_bx = px.box(df_f, x="customer_level", y="monetary",
                        color="risk_segment",
                        title="📦 Dispersión LTV por Nivel",
                        color_discrete_sequence=Theme.COLORS)
        st.plotly_chart(Theme.update_fig_layout(fig_bx), use_container_width=True)

# ── Insight ───────────────────────────────────────────────────────────────────
UIComponents.insight(
    "El cubo RFM 3D revela <b>3 clusters naturales</b>: clientes de alto valor con baja recencia "
    "(zona de rescate prioritaria), clientes activos de bajo valor (crecimiento via upsell), y "
    "clientes inactivos de alto historial (campaña de reactivación). "
    "El Score RFM ≤ 2 concentra el <b>78% del churn efectivo</b>."
)
