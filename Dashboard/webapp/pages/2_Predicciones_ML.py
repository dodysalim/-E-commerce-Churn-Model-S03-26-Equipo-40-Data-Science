import streamlit as st
import sys, os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components import Theme, UIComponents, ChartFactory
import plotly.express as px

st.set_page_config(page_title="P2 - ML Predicciones", layout="wide")
Theme.apply_global_css()
st.title("Página 2: ML Predicciones")

df_risk = st.session_state.get('df_risk', pd.DataFrame())
if df_risk.empty: st.stop()

# Row 1: Slicer
with st.container(border=True):
    risk_seg = st.multiselect("Riesgo (Segmentador)", df_risk['risk_segment'].unique(), default=df_risk['risk_segment'].unique())
df_r = df_risk[df_risk['risk_segment'].isin(risk_seg)]

# Row 2: 4 KPIs
c1, c2, c3, c4 = st.columns(4)
with c1: UIComponents.kpi("Avg Churn Prob", f"{df_r['churn_probability'].mean():.1f}%")
with c2: UIComponents.kpi("Max Riesgo Detectado", f"{df_r['churn_probability'].max():.1f}%")
with c3: UIComponents.kpi("Coeficiente LTV", f"${df_r['monetary'].median():,.0f}")
with c4: UIComponents.kpi("Varianza RFM", f"{df_r['rfm_score'].std():.1f}")

# Row 3: 3 Charts
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(ChartFactory.scatter(df_r, 'frequency', 'churn_probability', None, 'risk_segment', "Frecuencia vs Fuga"), use_container_width=True)
    with col2:
        df_f = pd.DataFrame({"Feature": ["Monto", "Recencia", "Frecuencia", "Score"], "SHAP": [0.4, 0.3, 0.2, 0.1]})
        st.plotly_chart(ChartFactory.bar(df_f, "SHAP", "Feature", orientation='h', title="Feature Importance (Sim)"), use_container_width=True)
    with col3:
        fig_v = px.violin(df_r, y="churn_probability", color="customer_level", box=True, title="Violín Densidad Fuga")
        st.plotly_chart(Theme.update_fig_layout(fig_v), use_container_width=True)

# Row 4: 2 Charts
with st.container():
    col4, col5 = st.columns([1, 1.5])
    with col4:
        st.plotly_chart(ChartFactory.heatmap(df_r, 'rfm_score', 'churn_probability', 'monetary', "Densidad LTV por Score ML"), use_container_width=True)
    with col5:
        fig_hist = px.histogram(df_r, x="churn_probability", color="risk_segment", title="Histograma Distribución Probabilidades", marginal="rug")
        st.plotly_chart(Theme.update_fig_layout(fig_hist), use_container_width=True)
