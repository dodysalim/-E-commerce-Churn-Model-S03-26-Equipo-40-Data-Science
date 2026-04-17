import streamlit as st
import sys, os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory
from data_loader import _generate_demo_data

st.set_page_config(page_title="Valor & Riesgo — Churn", page_icon="💰", layout="wide")
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
    <div style="background:linear-gradient(135deg,#F59E0B,#D97706); width:42px; height:42px;
                border-radius:10px; display:flex; align-items:center; justify-content:center;
                font-size:1.4rem;">💰</div>
    <div>
        <h2 style="margin:0; font-size:1.4rem; color:#1A202C; font-weight:800;">Matriz de Valor y Riesgo</h2>
        <div style="font-size:0.75rem; color:#64748B;">
            Exposición financiera · LTV en riesgo · Mapa de calor por segmento
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Slicers ───────────────────────────────────────────────────────────────────
with st.container(border=True):
    col_x, col_y = st.columns(2)
    lvls = list(df_risk["customer_level"].unique())
    lvl  = col_x.multiselect("👤 Nivel de Cliente", lvls, default=lvls)
    segs = list(df_risk["risk_segment"].unique())
    seg  = col_y.multiselect("⚠️ Segmento de Riesgo", segs, default=segs)

df_r = df_risk[df_risk["customer_level"].isin(lvl) & df_risk["risk_segment"].isin(seg)]

# ── KPIs ──────────────────────────────────────────────────────────────────────
UIComponents.section("Exposición Financiera por Segmento")
c1, c2, c3, c4 = st.columns(4)
total_exp   = df_r["monetary"].sum()
opp_cost    = df_r[df_r["churn_probability"] > 60]["monetary"].sum()
avg_ltv     = df_r["monetary"].mean()
high_count  = len(df_r[df_r["churn_probability"] > 60])

with c1: UIComponents.kpi("Cartera Total",        f"${total_exp:,.0f}",  "Valor acumulado filtrado", "blue")
with c2: UIComponents.kpi("LTV en Riesgo Crítico", f"${opp_cost:,.0f}",  f"{high_count} clientes >60%", "red")
with c3: UIComponents.kpi("LTV Promedio",          f"${avg_ltv:,.0f}",   "Por cliente seleccionado", "yellow")
with c4: UIComponents.kpi("Costo Oportunidad",     f"${opp_cost*0.18:,.0f}", "Estimado 18% LTV rescatable", "green")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
UIComponents.section("Mapa de Zonas de Riesgo")
col1, col2 = st.columns([2, 1])

with col1:
    fig = ChartFactory.treemap(df_r, [px.Constant("Portafolio"), "risk_segment", "customer_level"],
                               "monetary", "churn_probability",
                               "🗺️ Treemap: Valor Expuesto por Zona de Riesgo")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df_radar = df_r.groupby("risk_segment")[["monetary", "recency", "frequency"]].mean()
    if not df_radar.empty:
        df_radar_norm = df_radar / df_radar.max()
        fig = go.Figure()
        colors = ["#EF4444", "#F59E0B", "#10B981"]

        def _hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
            """Convierte '#RRGGBB' → 'rgba(r,g,b,alpha)' correctamente."""
            h = hex_color.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"

        for i, (idx, row) in enumerate(df_radar_norm.iterrows()):
            c = colors[i % len(colors)]
            fig.add_trace(go.Scatterpolar(
                r=row.values.tolist() + [row.values[0]],
                theta=list(row.index) + [row.index[0]],
                fill="toself", name=idx,
                line=dict(color=c, width=2),
                fillcolor=_hex_to_rgba(c, 0.15),
            ))
        fig.update_layout(
            polar=dict(bgcolor=Theme.TILE_BG, radialaxis=dict(visible=True, range=[0, 1])),
            paper_bgcolor=Theme.TILE_BG, font_color=Theme.TEXT_COLOR,
            title="📡 Polígono de Severidad por Segmento", height=340,
            title_font=dict(size=13),
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
UIComponents.section("Proyección Financiera")
col3, col4, col5 = st.columns(3)

with col3:
    base   = df_r["monetary"].sum()
    fugas  = -df_r[df_r["churn_probability"] > 70]["monetary"].sum()
    rescate = abs(fugas) * 0.35
    w_df = pd.DataFrame({
        "Fase":    ["Base LTV",  "Pérdida Estimada", "Rescate Potencial"],
        "Val":     [base,        fugas,               rescate],
        "Medida":  ["absolute",  "relative",          "relative"],
    })
    fig_w = go.Figure(go.Waterfall(
        x=w_df["Fase"], y=w_df["Val"], measure=w_df["Medida"],
        connector={"line": {"color": "#CBD5E1"}},
        increasing={"marker": {"color": "#10B981"}},
        decreasing={"marker": {"color": "#EF4444"}},
        totals={"marker": {"color": "#4F46E5"}},
        text=[f"${abs(v):,.0f}" for v in w_df["Val"]],
        textposition="outside",
    ))
    fig_w.update_layout(title="💧 Cascada de Exposición LTV", height=340,
                        title_font=dict(size=13))
    st.plotly_chart(Theme.update_fig_layout(fig_w), use_container_width=True)

with col4:
    fig = ChartFactory.area(df_r.sort_values("churn_probability"),
                            "churn_probability", "monetary", "risk_segment",
                            "📈 Área: Valor Acumulado vs Probabilidad de Fuga")
    st.plotly_chart(fig, use_container_width=True)

with col5:
    df_bars = df_r.groupby("risk_segment")["monetary"].sum().reset_index()
    fig = ChartFactory.bar(df_bars, "risk_segment", "monetary", "risk_segment",
                           "💼 LTV Total por Nivel de Riesgo")
    st.plotly_chart(fig, use_container_width=True)

UIComponents.insight(
    f"La cartera total en análisis es de <b>${total_exp:,.0f}</b>. "
    f"El escenario pesimista proyecta una pérdida de <b>${abs(fugas):,.0f}</b> si no se actúa. "
    f"Aplicando estrategias de rescate, se estima recuperar hasta <b>${rescate:,.0f}</b> "
    f"(35% del valor en fuga), con retorno positivo en 90 días."
)
