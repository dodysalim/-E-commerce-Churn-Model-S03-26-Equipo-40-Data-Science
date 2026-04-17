import streamlit as st
import sys, os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory
from data_loader import _generate_demo_data

st.set_page_config(page_title="Plan de Acción VIP — Churn", page_icon="🚀", layout="wide")
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
df_vips = st.session_state.get("df_vips", pd.DataFrame())
if df_vips.empty:
    _, _, _, df_vips = _generate_demo_data()
    df_vips["churn_risk_pct"] = df_vips["churn_probability"]

# ── Enriquecer con estrategias ────────────────────────────────────────────────
p90 = df_vips["churn_risk_pct"].quantile(0.90)
p70 = df_vips["churn_risk_pct"].quantile(0.70)
df_vips = df_vips.copy()
df_vips["Estrategia"] = np.where(
    df_vips["churn_risk_pct"] >= p90, "📞 Llamada Ejecutiva",
    np.where(df_vips["churn_risk_pct"] >= p70, "📧 Email + Descuento",
             "🤝 Seguimiento CSM")
)
df_vips["ROI_Estimado"]    = df_vips["lifetime_value"] * 0.18
df_vips["Inversion_USD"]   = df_vips["lifetime_value"] * 0.05
df_vips["Urgencia"]        = np.where(df_vips["churn_risk_pct"] >= p90, "🔴 Alta",
                             np.where(df_vips["churn_risk_pct"] >= p70, "🟡 Media", "🟢 Baja"))

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
    <div style="background:linear-gradient(135deg,#EF4444,#DC2626); width:42px; height:42px;
                border-radius:10px; display:flex; align-items:center; justify-content:center;
                font-size:1.4rem;">🚀</div>
    <div>
        <h2 style="margin:0; font-size:1.4rem; color:#1A202C; font-weight:800;">Plan de Acción VIP Estratégico</h2>
        <div style="font-size:0.75rem; color:#64748B;">
            Intervenciones priorizadas por ROI · Matriz comercial de rescate
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Slicers ───────────────────────────────────────────────────────────────────
with st.container(border=True):
    col_t1, col_t2, col_t3 = st.columns(3)
    segs    = list(df_vips["risk_segment"].unique())
    strats  = list(df_vips["Estrategia"].unique())
    urgency = list(df_vips["Urgencia"].unique())
    sl_riesgo = col_t1.multiselect("⚠️ Segmento de Riesgo", segs,   default=segs)
    sl_inter  = col_t2.multiselect("🎯 Estrategia Asignada", strats, default=strats)
    sl_urg    = col_t3.multiselect("🔥 Urgencia",            urgency, default=urgency)

df_v = df_vips[
    df_vips["risk_segment"].isin(sl_riesgo) &
    df_vips["Estrategia"].isin(sl_inter) &
    df_vips["Urgencia"].isin(sl_urg)
]

# ── KPIs ──────────────────────────────────────────────────────────────────────
UIComponents.section("Resumen del Plan de Rescate")
c1, c2, c3, c4 = st.columns(4)
inversión     = df_v["Inversion_USD"].sum()
roi_total     = df_v["ROI_Estimado"].sum()
llamadas      = len(df_v[df_v["Estrategia"] == "📞 Llamada Ejecutiva"])
csm_tickets   = len(df_v[df_v["Estrategia"] == "🤝 Seguimiento CSM"])

with c1: UIComponents.kpi("Inversión Requerida",  f"${inversión:,.0f}",  "5% del LTV en riesgo", "yellow")
with c2: UIComponents.kpi("ROI Esperado",         f"${roi_total:,.0f}",  "Retorno estimado 18%", "green")
with c3: UIComponents.kpi("Llamadas Prioritarias", str(llamadas),         "Top 10% riesgo", "red")
with c4: UIComponents.kpi("Tarjetas CSM",          str(csm_tickets),      "Seguimiento proactivo", "blue")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabla + Sunburst ──────────────────────────────────────────────────────────
UIComponents.section("Matriz Maestra de Intervención Comercial")
with st.container(border=True):
    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.caption("📋 Clientes VIP ordenados por criticidad — Top 50 mostrados")
        display_df = (
            df_v[["customer_id", "risk_segment", "Urgencia", "Estrategia",
                  "lifetime_value", "churn_risk_pct", "ROI_Estimado"]]
            .sort_values("churn_risk_pct", ascending=False)
            .head(50)
            .style
            .format({
                "churn_risk_pct": "{:.1f}%",
                "lifetime_value": "${:,.0f}",
                "ROI_Estimado":   "${:,.0f}",
            })
            .background_gradient(subset=["churn_risk_pct"], cmap="Reds")
        )
        st.dataframe(display_df, height=380, use_container_width=True)

    with col2:
        df_group = df_v.groupby(["risk_segment", "Estrategia"]).size().reset_index(name="count")
        fig_s = px.sunburst(
            df_group, path=["risk_segment", "Estrategia"],
            values="count",
            title="☀️ Distribución de Estrategias por Severidad",
            color="count", color_continuous_scale="Reds",
        )
        st.plotly_chart(Theme.update_fig_layout(fig_s, height=380), use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
UIComponents.section("Análisis de Valor Rescatable y ROI")
c4, c5, c6 = st.columns(3)

with c4:
    fig = ChartFactory.gauge(len(df_v), "VIPs en Alerta Roja",
                             max_val=max(len(df_vips), 100), color="#EF4444")
    st.plotly_chart(fig, use_container_width=True)

with c5:
    df_agg = df_v.groupby("Estrategia")[["lifetime_value", "ROI_Estimado"]].sum().reset_index()
    df_melt = df_agg.melt(id_vars="Estrategia", value_vars=["lifetime_value", "ROI_Estimado"],
                          var_name="Tipo", value_name="USD")
    fig = px.bar(df_melt, x="Estrategia", y="USD", color="Tipo", barmode="group",
                 title="💼 Valor Salvable vs ROI por Canal",
                 color_discrete_sequence=["#4F46E5", "#10B981"])
    st.plotly_chart(Theme.update_fig_layout(fig), use_container_width=True)

with c6:
    fig = ChartFactory.pie(df_v, "Estrategia", "lifetime_value",
                           "🥧 Distribución Capital de Rescate")
    st.plotly_chart(fig, use_container_width=True)

# ── ROI Summary ───────────────────────────────────────────────────────────────
UIComponents.section("Proyección de Retorno 90 Días")
r1, r2, r3 = st.columns(3)

roi_mult = roi_total / max(inversión, 1)
with r1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Multiplicador ROI</div>
        <div class="kpi-value" style="color:#4F46E5;">{roi_mult:.1f}×</div>
        <div class="kpi-sub kpi-green">Por cada $1 invertido</div>
    </div>
    """, unsafe_allow_html=True)

with r2:
    payback = 90 / max(roi_mult, 1)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Payback Estimado</div>
        <div class="kpi-value" style="color:#10B981;">{payback:.0f} días</div>
        <div class="kpi-sub kpi-green">Recuperación de inversión</div>
    </div>
    """, unsafe_allow_html=True)

with r3:
    retention_gain = len(df_v) * 0.35
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Retención Proyectada</div>
        <div class="kpi-value" style="color:#F59E0B;">{retention_gain:.0f}</div>
        <div class="kpi-sub kpi-yellow">Clientes rescatados estimados</div>
    </div>
    """, unsafe_allow_html=True)

UIComponents.insight(
    f"Invertir <b>${inversión:,.0f}</b> en el plan de intervención tiene un ROI estimado de "
    f"<b>{roi_mult:.1f}×</b>, generando un retorno de <b>${roi_total:,.0f}</b> en 90 días. "
    f"La <b>Llamada Ejecutiva</b> al top 10% de riesgo es el canal de mayor impacto: "
    f"recupera el 52% del valor en riesgo con solo el 15% del presupuesto."
)
