import streamlit as st
from data_loader import get_repository, _generate_demo_data
from components import Theme

st.set_page_config(
    page_title="No Country — Churn Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
Theme.apply_global_css()

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <div style="font-size:2.2rem;">📊</div>
        <div style="font-size:1.1rem; font-weight:700; color:#C7D2FE; letter-spacing:1px;">
            CHURN INTELLIGENCE
        </div>
        <div style="font-size:0.7rem; color:#818CF8; letter-spacing:2px; margin-top:2px;">
            NO COUNTRY · EQUIPO 40
        </div>
    </div>
    <hr style="border-color:#4338CA; margin:10px 0 20px 0;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.72rem; color:#A5B4FC; text-transform:uppercase; letter-spacing:1px;
                font-weight:600; margin-bottom:8px;">
        Módulos de Análisis
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.82rem; color:#C7D2FE; line-height:2.0; padding-left:8px;">
        📋 <b>Resumen Ejecutivo</b><br>
        🤖 <b>Predicciones ML</b><br>
        💰 <b>Valor & Riesgo</b><br>
        🎯 <b>Segmentación RFM</b><br>
        🚀 <b>Plan de Acción</b>
    </div>
    <hr style="border-color:#4338CA; margin:20px 0;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.72rem; color:#6366F1; text-align:center;">
        Sprint 3 · E-Commerce Churn<br>
        Dataset: UCI Online Retail II<br>
        ~1M transacciones analizadas
    </div>
    """, unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 60px 0 40px 0;">
    <div style="display:inline-block; background:linear-gradient(135deg,#4F46E5,#7C3AED);
                padding:8px 22px; border-radius:30px; margin-bottom:22px;">
        <span style="color:#fff; font-size:0.78rem; font-weight:600; letter-spacing:2px;">
            NO COUNTRY · EQUIPO 40 · SPRINT 3
        </span>
    </div>
    <h1 style="font-size:3rem; font-weight:800; color:#1A202C; margin:0; line-height:1.15;
               font-family:'Inter',sans-serif;">
        Loyalty &amp; Retention<br>
        <span style="background:linear-gradient(135deg,#4F46E5,#10B981);
                     -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            Intelligence Platform
        </span>
    </h1>
    <p style="color:#64748B; font-size:1.05rem; max-width:620px; margin:20px auto; line-height:1.7;">
        Motor analítico predictivo que detecta clústeres de clientes en riesgo de abandono
        usando Machine Learning, y genera estrategias de retención personalizadas con impacto financiero real.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

cards = [
    ("🤖", "#4F46E5", "01 — ML Predictivo",   "XGBoost + Random Forest con SHAP interpretability"),
    ("💰", "#10B981", "02 — Valor Expuesto",   "LTV calculado por segmento y cuantificación del riesgo"),
    ("🎯", "#F59E0B", "03 — RFM 3D",           "Clustering espacial Recency · Frequency · Monetary"),
    ("🚀", "#EF4444", "04 — Plan de Acción",   "Intervenciones priorizadas por ROI estimado"),
]

for col, (icon, color, title, desc) in zip([col1, col2, col3, col4], cards):
    with col:
        st.markdown(f"""
        <div style="background:#fff; border-radius:14px; padding:24px 18px; text-align:center;
                    border:1px solid #E2E8F0; box-shadow:0 4px 6px -1px rgba(0,0,0,0.07);
                    transition:transform .2s;">
            <div style="font-size:2rem; margin-bottom:10px;">{icon}</div>
            <div style="font-size:0.72rem; font-weight:700; color:{color};
                        text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">
                {title}
            </div>
            <div style="font-size:0.83rem; color:#64748B; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Tech Stack ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:16px; background:#fff; border-radius:12px;
            border:1px solid #E2E8F0;">
    <div style="font-size:0.7rem; color:#94A3B8; text-transform:uppercase;
                letter-spacing:1.5px; margin-bottom:10px; font-weight:600;">
        Stack Tecnológico
    </div>
    <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
        <span style="background:#EEF2FF;color:#4338CA;padding:5px 14px;border-radius:20px;
                     font-size:0.78rem;font-weight:600;">Python 3.11</span>
        <span style="background:#FEF3C7;color:#92400E;padding:5px 14px;border-radius:20px;
                     font-size:0.78rem;font-weight:600;">XGBoost</span>
        <span style="background:#DCFCE7;color:#166534;padding:5px 14px;border-radius:20px;
                     font-size:0.78rem;font-weight:600;">Supabase</span>
        <span style="background:#EEF2FF;color:#4338CA;padding:5px 14px;border-radius:20px;
                     font-size:0.78rem;font-weight:600;">Streamlit</span>
        <span style="background:#FEE2E2;color:#991B1B;padding:5px 14px;border-radius:20px;
                     font-size:0.78rem;font-weight:600;">Scikit-learn</span>
        <span style="background:#F0FDF4;color:#15803D;padding:5px 14px;border-radius:20px;
                     font-size:0.78rem;font-weight:600;">SHAP</span>
        <span style="background:#FDF4FF;color:#7E22CE;padding:5px 14px;border-radius:20px;
                     font-size:0.78rem;font-weight:600;">Plotly</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-top:30px;">
    <p style="color:#94A3B8; font-size:0.82rem; letter-spacing:1px;">
        ← Seleccione un módulo en el panel lateral para iniciar el análisis
    </p>
</div>
""", unsafe_allow_html=True)

# ── Precargar datos en session_state ─────────────────────────────────────────
with st.spinner("Inicializando plataforma de datos…"):
    repo = get_repository()

    df_dist   = repo.fetch_table("v_customer_distribution")
    df_global = repo.fetch_table("v_global_metrics")
    df_risk   = repo.fetch_table("v_value_risk_matrix")
    df_vips   = repo.fetch_table("v_vips_at_risk")

    # Fallback a datos demo si Supabase no está disponible
    if df_dist.empty or df_global.empty or df_risk.empty:
        df_dist, df_global, df_risk, df_vips = _generate_demo_data()
        st.toast("📊 Modo demo activado — datos simulados realistas cargados", icon="ℹ️")

    st.session_state["df_global"] = df_global
    st.session_state["df_dist"]   = df_dist
    st.session_state["df_risk"]   = df_risk
    st.session_state["df_vips"]   = df_vips
