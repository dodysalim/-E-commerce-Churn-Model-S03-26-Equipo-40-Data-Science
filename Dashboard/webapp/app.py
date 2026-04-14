import streamlit as st
from data_loader import get_repository
from components import Theme

st.set_page_config(page_title="Enterprise Churn Dashboard PRO", page_icon="📈", layout="wide")
Theme.apply_global_css()

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3256/3256086.png", width=60)
st.sidebar.title("Bienvenido")
st.sidebar.markdown(
    "Selecciona un módulo en el menú de la izquierda para navegar por las métricas de Churn E-commerce."
)

# Portada Elegante y Empresarial
st.markdown("""
<div style="text-align: center; margin-top: 80px; margin-bottom: 50px; animation: fadeIn 1.5s;">
    <h1 style="font-size: 3.5rem; font-weight: 800; color: #1F2937; margin-bottom: 10px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        Loyalty & Retention Intelligence
    </h1>
    <h3 style="font-size: 1.5rem; font-weight: 400; color: #6B7280; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        Plataforma Predictiva de Fuga de Clientes (Churn Insights)
    </h3>
    <p style="color: #6B7280; font-size: 1.1rem; max-width: 680px; margin: 25px auto; line-height: 1.6;">
        Motor analítico avanzado para monitorear el ciclo de vida de los clientes, detectar clústeres en riesgo mediante Machine Learning y desplegar estrategias financieras de rescate comercial en tiempo real.
    </p>
</div>

<div style="display: flex; gap: 20px; justify-content: center; margin-top: 40px; flex-wrap: wrap;">
    <div class="kpi-card" style="width: 250px; padding: 30px 20px;">
        <h4 style="color: #10B981; font-size: 2rem; margin-bottom: 10px;">01</h4>
        <p style="color: #1F2937; font-size: 1.1rem; font-weight: 600;">Diagnóstico ML</p>
        <p style="color: #6B7280; font-size: 0.85rem; margin-top: 5px;">Aislamiento probabilístico de fuga estructural</p>
    </div>
    <div class="kpi-card" style="width: 250px; padding: 30px 20px;">
        <h4 style="color: #3B82F6; font-size: 2rem; margin-bottom: 10px;">02</h4>
        <p style="color: #1F2937; font-size: 1.1rem; font-weight: 600;">Valor Expuesto</p>
        <p style="color: #6B7280; font-size: 0.85rem; margin-top: 5px;">Mapeo transaccional LTV vs Riesgo</p>
    </div>
    <div class="kpi-card" style="width: 250px; padding: 30px 20px;">
        <h4 style="color: #F59E0B; font-size: 2rem; margin-bottom: 10px;">03</h4>
        <p style="color: #1F2937; font-size: 1.1rem; font-weight: 600;">Segmentación RFM</p>
        <p style="color: #6B7280; font-size: 0.85rem; margin-top: 5px;">Enrutamiento táctico y retención automatizada</p>
    </div>
</div>

<div style="text-align: center; margin-top: 60px;">
    <p style="color: #94A3B8; font-size: 0.9rem; letter-spacing: 1px;">
        &larr; UTILICE EL PANEL LATERAL PARA NAVEGAR ENTRE LOS MÓDULOS DE INTELIGENCIA
    </p>
</div>
""", unsafe_allow_html=True)

# Precargar datos e hidratar el session state para que las páginas hijas no consuman doble carga
with st.spinner("Inicializando modelo de datos global..."):
    repo = get_repository()
    st.session_state['df_global'] = repo.fetch_table('v_global_metrics')
    st.session_state['df_dist'] = repo.fetch_table('v_customer_distribution')
    st.session_state['df_risk'] = repo.fetch_table('v_value_risk_matrix')
    st.session_state['df_vips'] = repo.fetch_table('v_vips_at_risk')
