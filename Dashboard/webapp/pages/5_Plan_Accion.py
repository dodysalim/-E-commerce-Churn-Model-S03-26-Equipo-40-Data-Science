import streamlit as st
import sys, os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory

st.set_page_config(page_title="P5 - Intervencion", layout="wide")
Theme.apply_global_css()
st.title("Página 5: Plan de Acción VIP Estratégico")
df_vips = st.session_state.get('df_vips', pd.DataFrame())
if df_vips.empty: st.stop()

# Expand dataset with mock strategies (Splitting 3 ways based on top decile risk)
p90 = df_vips['churn_risk_pct'].quantile(0.90)
p70 = df_vips['churn_risk_pct'].quantile(0.70)
df_vips['Intervencion'] = np.where(df_vips['churn_risk_pct'] >= p90, "Llamada Ejecutiva", 
                          np.where(df_vips['churn_risk_pct'] >= p70, "Email Descuento", "Seguimiento CSM"))
df_vips['ROI_Estimado'] = df_vips['lifetime_value'] * 0.15

# Segmentadores / Slicers
with st.container(border=True):
    col_t1, col_t2 = st.columns(2)
    sl_riesgo = col_t1.multiselect("Riesgo (Segmentador)", df_vips['risk_segment'].unique(), default=df_vips['risk_segment'].unique())
    sl_inter = col_t2.multiselect("Estrategia Asignada", df_vips['Intervencion'].unique(), default=df_vips['Intervencion'].unique())

df_vips = df_vips[(df_vips['risk_segment'].isin(sl_riesgo)) & (df_vips['Intervencion'].isin(sl_inter))]

# 3 KPIs
c1, c2, c3 = st.columns(3)
with c1: UIComponents.kpi("Presupuesto Intervención", f"${df_vips['ROI_Estimado'].sum()/0.15 * 0.05:,.0f}", "5% de inversión LTV")
with c2: UIComponents.kpi("Tarjeas Asignadas CSM", str(len(df_vips[df_vips['Intervencion'] == 'Seguimiento CSM'])))
with c3: UIComponents.kpi("Llamadas Alta Prioridad", str(len(df_vips[df_vips['Intervencion'] == 'Llamada Ejecutiva'])))

with st.container(border=True):
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("### Matriz Maestra Comercial R01")
        st.dataframe(df_vips[['customer_id', 'risk_segment', 'Intervencion', 'lifetime_value', 'churn_risk_pct']]
                     .sort_values(by="churn_risk_pct", ascending=False)
                     .style.format({"churn_risk_pct": "{:.1f}%", "lifetime_value": "${:,.0f}"})
                     .background_gradient(subset=["churn_risk_pct"], cmap="Reds"), height=380, use_container_width=True)
    with col2:
        df_group = df_vips.groupby(['risk_segment', 'Intervencion']).size().reset_index(name='count')
        fig_s = px.sunburst(df_group, path=['risk_segment', 'Intervencion'], values='count', title="Distribución de Estrategias por Severidad", color='count', color_continuous_scale="Reds")
        st.plotly_chart(Theme.update_fig_layout(fig_s), use_container_width=True)

with st.container():
    c4, c5, c6 = st.columns(3)
    with c4:
        st.plotly_chart(ChartFactory.gauge(len(df_vips), "VIPs Riesgo (Alerta Roja)", 500), use_container_width=True)
    with c5:
        df_agg = df_vips.groupby("Intervencion")["lifetime_value"].sum().reset_index()
        st.plotly_chart(ChartFactory.bar(df_agg, "Intervencion", "lifetime_value", "Intervencion", "Valor Salvable por Canal"), use_container_width=True)
    with c6:
        st.plotly_chart(ChartFactory.pie(df_vips, "Intervencion", "lifetime_value", "Distribución Capital Rescate"), use_container_width=True)
