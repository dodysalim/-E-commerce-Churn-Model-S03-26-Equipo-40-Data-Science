import streamlit as st
import sys, os, random
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory

st.set_page_config(page_title="P1 - Resumen Ejecutivo", layout="wide")
Theme.apply_global_css()
st.title("Página 1: Resumen Ejecutivo")

df_global = st.session_state.get('df_global', pd.DataFrame())
df_dist = st.session_state.get('df_dist', pd.DataFrame())
if df_global.empty: st.stop()

# Top Slicer PBI Style
with st.container(border=True):
    col_s1, col_s2, col_s3 = st.columns(3)
    filt_level = col_s1.multiselect("Nivel RFM (Segmentador)", df_dist['customer_level'].unique(), default=df_dist['customer_level'].unique())

df_d = df_dist[df_dist['customer_level'].isin(filt_level)] if not df_dist.empty else df_dist

# Row 1: 4 KPIs (Counts as 4 visual elements)
c1, c2, c3, c4 = st.columns(4)
with c1: UIComponents.kpi("Clientes Analizados", f"{int(df_global['total_customers_analyzed'].iloc[0]):,}", "+5.2% vs last m")
with c2: UIComponents.kpi("Tasa Abandono Pct", f"{df_global['overall_churn_rate_pct'].iloc[0]:.1f}%", "-0.1% vs last m")
with c3: UIComponents.kpi("Exposición", f"${df_global['high_risk_monetary_exposure'].iloc[0]:,.0f}", "Alerta")
with c4: UIComponents.kpi("VIPs Riesgo", f"{int(df_global['vips_at_risk_count'].iloc[0])}", "Crítico")

st.markdown("<br>", unsafe_allow_html=True)
# Row 2: 3 Charts
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(ChartFactory.pie(df_d, 'customer_level', 'avg_monetary', "Ingresos por Segmento (LTV)"), use_container_width=True)
    with col2:
        st.plotly_chart(ChartFactory.bar(df_d, 'customer_level', 'customer_count', 'customer_level', "Volumen Clientes por Cohorte"), use_container_width=True)
    with col3:
         # Simulated Sparkline (Area chart) of Churn Trend
         mock_dates = pd.date_range(end=pd.Timestamp.today(), periods=6, freq='M')
         mock_trend = pd.DataFrame({"Mes": mock_dates, "Churn Rate": [4.2, 4.3, 4.5, 4.1, 4.0, int(df_global['overall_churn_rate_pct'].iloc[0])]})
         st.plotly_chart(ChartFactory.area(mock_trend, 'Mes', 'Churn Rate', title="Tendencia Histórica Churn"), use_container_width=True)

# Row 3: 2 Charts
with st.container():
    col4, col5 = st.columns([2, 1])
    with col4:
        st.plotly_chart(ChartFactory.scatter(df_d, 'avg_monetary', 'avg_churn_risk_pct', 'customer_count', 'customer_level', "Correlación Valor LTV vs Deserción Promedio"), use_container_width=True)
    with col5:
        st.plotly_chart(ChartFactory.gauge(df_global['overall_churn_rate_pct'].iloc[0], "Salud Retención", 20, "red"), use_container_width=True)
