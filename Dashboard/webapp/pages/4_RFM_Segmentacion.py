import streamlit as st
import sys, os
import pandas as pd
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory

st.set_page_config(page_title="P4 - Segmentacion RFM", layout="wide")
Theme.apply_global_css()
st.title("Página 4: Insight de Segmentación (RFM)")
df_risk = st.session_state.get('df_risk', pd.DataFrame())
df_dist = st.session_state.get('df_dist', pd.DataFrame())
if df_risk.empty: st.stop()

# Segmentadores / Slicers
with st.container(border=True):
    filtro_riesgo = st.multiselect("Nivel de Riesgo (Segmentador)", df_risk['risk_segment'].unique(), default=df_risk['risk_segment'].unique())
df_risk = df_risk[df_risk['risk_segment'].isin(filtro_riesgo)]

# 3 KPIs
c1, c2, c3 = st.columns(3)
with c1: UIComponents.kpi("Avg Recency", f"{df_risk['recency'].mean():.1f} días")
with c2: UIComponents.kpi("Avg Freq", f"{df_risk['frequency'].mean():.1f} tx")
with c3: UIComponents.kpi("Avg Monetary", f"${df_risk['monetary'].mean():,.0f}")

with st.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(ChartFactory.funnel(df_dist.sort_values(by="customer_count", ascending=False), "customer_count", "customer_level", "Embudo Demográfico"), use_container_width=True)
        st.plotly_chart(ChartFactory.bar(df_risk.groupby("rfm_score").size().reset_index(name="C"), "rfm_score", "C", title="Densidad por Puntaje RFM"), use_container_width=True)
        
        fig_s = px.sunburst(df_risk, path=['rfm_score', 'customer_level'], values='monetary', title="Flujo Multinivel RFM")
        st.plotly_chart(Theme.update_fig_layout(fig_s), use_container_width=True)

    with col2:
        fig_3d = px.scatter_3d(df_risk, x='recency', y='frequency', z='monetary', color='customer_level', size='rfm_score', title="Cubo Espacial de Clustering RFM 360", size_max=10)
        fig_3d.update_layout(scene=dict(xaxis_title='Recency', yaxis_title='Freq', zaxis_title='Valor USD'), paper_bgcolor=Theme.TILE_BG, font_color="#1F2937", height=450)
        st.plotly_chart(fig_3d, use_container_width=True)
        
        # Llenar el espacio en blanco debajo del Cubo 3D
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            st.plotly_chart(ChartFactory.scatter(df_risk, 'recency', 'frequency', None, 'risk_segment', "Recency vs Freq"), use_container_width=True)
        with c_sub2:
            fig_bx = px.box(df_risk, x="customer_level", y="monetary", color="risk_segment", title="Dispersión Outliers Monetary")
            st.plotly_chart(Theme.update_fig_layout(fig_bx), use_container_width=True)
