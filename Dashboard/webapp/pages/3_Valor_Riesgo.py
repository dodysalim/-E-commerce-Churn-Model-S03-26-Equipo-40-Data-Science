import streamlit as st
import sys, os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory

st.set_page_config(page_title="P3 - Matriz Exposicion", layout="wide")
Theme.apply_global_css()
st.title("Página 3: Matriz de Valor y Riesgo")
df_risk = st.session_state.get('df_risk', pd.DataFrame())
if df_risk.empty: st.stop()

with st.container(border=True):
    col_x, col_y = st.columns(2)
    lvl = col_x.multiselect("Filtro: Nivel", df_risk['customer_level'].unique(), default=df_risk['customer_level'].unique())
    df_r = df_risk[df_risk['customer_level'].isin(lvl)]

c1, c2, c3 = st.columns(3)
with c1: UIComponents.kpi("Total Clientes", str(len(df_r)))
with c2: UIComponents.kpi("Valor Expuesto M", f"${df_r['monetary'].sum()/1000000:.2f}M")
with c3: UIComponents.kpi("Costo Oportunidad", f"${df_r['monetary'].mean()*len(df_r)*0.1:,.0f}")

with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(ChartFactory.treemap(df_r, [px.Constant("Hub"), 'risk_segment', 'customer_level'], 'monetary', 'churn_probability', "Treemap de Zonas de Peligro"), use_container_width=True)
    with col2:
        df_radar = df_r.groupby('risk_segment')[['monetary', 'recency', 'frequency']].mean()
        df_radar = df_radar / df_radar.max()
        fig = go.Figure()
        for i, row in df_radar.iterrows():
            fig.add_trace(go.Scatterpolar(r=row.values, theta=row.index, fill='toself', name=i))
        fig.update_layout(polar=dict(bgcolor=Theme.TILE_BG), paper_bgcolor='rgba(0,0,0,0)', font_color=Theme.TEXT_COLOR, title="Polígonos de Severidad")
        st.plotly_chart(fig, use_container_width=True)

with st.container():
    col3, col4, col5 = st.columns(3)
    with col3:
        w_df = pd.DataFrame({"Fase": ["Base", "Ventas", "Fugas Estim."], "Val": [df_r['monetary'].sum(), 150000, -df_r[df_r['churn_probability']>70]['monetary'].sum()]})
        fig_w = go.Figure(go.Waterfall(x=w_df['Fase'], y=w_df['Val'], measure=["absolute","relative","relative"]))
        fig_w.update_layout(title="Cascada Exposición LTV")
        st.plotly_chart(Theme.update_fig_layout(fig_w), use_container_width=True)
    with col4:
        st.plotly_chart(ChartFactory.area(df_r.sort_values("churn_probability"), 'churn_probability', 'monetary', 'risk_segment', "Área Fugas Proyectiva"), use_container_width=True)
    with col5:
        df_bars = df_r.groupby("risk_segment")["monetary"].sum().reset_index()
        st.plotly_chart(ChartFactory.bar(df_bars, 'risk_segment', 'monetary', orientation='v', title="Montos por Nivel Riesgo"), use_container_width=True)
