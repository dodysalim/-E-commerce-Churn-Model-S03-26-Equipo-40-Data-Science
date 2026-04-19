from supabase import create_client, Client
import pandas as pd
import numpy as np
import streamlit as st

# ──────────────────────────────────────────────
#  DEMO DATA — se activa si Supabase no responde
# ──────────────────────────────────────────────
def _generate_demo_data():
    """Genera datos realistas para demostración offline."""
    np.random.seed(42)
    N = 800

    levels   = ["VIP Platino", "VIP Oro", "Cliente Activo", "Cliente Ocasional", "Cliente Inactivo"]
    segments = ["Alto Riesgo", "Riesgo Medio", "Bajo Riesgo"]

    # ── v_customer_distribution ──────────────────
    dist_rows = []
    for lvl, count, mon, churn in zip(
        levels,
        [45, 120, 280, 220, 135],
        [12500, 5800, 2100, 850, 340],
        [22, 30, 18, 10, 5],
    ):
        dist_rows.append({
            "customer_level":    lvl,
            "customer_count":    count,
            "avg_monetary":      mon,
            "avg_churn_risk_pct": churn,
        })
    df_dist = pd.DataFrame(dist_rows)

    # ── v_global_metrics ────────────────────────
    df_global = pd.DataFrame([{
        "total_customers_analyzed":  800,
        "overall_churn_rate_pct":    4.2,
        "high_risk_monetary_exposure": 387_420,
        "vips_at_risk_count":        31,
    }])

    # ── v_value_risk_matrix ──────────────────────
    risk_df = pd.DataFrame({
        "customer_id":    [f"C{str(i).zfill(4)}" for i in range(N)],
        "customer_level": np.random.choice(levels, N, p=[0.06, 0.15, 0.35, 0.28, 0.16]),
        "risk_segment":   np.random.choice(segments, N, p=[0.25, 0.45, 0.30]),
        "recency":        np.random.randint(1, 180, N),
        "frequency":      np.random.randint(1, 50, N),
        "monetary":       np.random.lognormal(7.5, 1.2, N),
        "rfm_score":      np.random.randint(1, 6, N),
        "churn_probability": np.random.beta(2, 5, N) * 100,
        "lifetime_value": np.random.lognormal(8.0, 1.1, N),
    })
    risk_df["churn_probability"] = risk_df["churn_probability"].clip(1, 99).round(1)

    # ── v_vips_at_risk ───────────────────────────
    vip_mask = (risk_df["customer_level"].isin(["VIP Platino", "VIP Oro"])) & \
               (risk_df["churn_probability"] > 45)
    df_vips = risk_df[vip_mask].copy().head(80)
    df_vips["churn_risk_pct"] = df_vips["churn_probability"]

    return df_dist, df_global, risk_df, df_vips


class SupabaseRepository:
    """Single Responsibility: Manejar la conexión a Supabase y extraer datasets."""

    def __init__(self, url: str, key: str):
        self.url    = url
        self.key    = key
        self.client: Client = None
        self._demo_mode = False

    def connect(self):
        try:
            self.client = create_client(self.url, self.key)
        except Exception:
            self._demo_mode = True
        return self

    @st.cache_data(ttl=900, show_spinner=False)
    def fetch_table(_self, table_name: str) -> pd.DataFrame:
        """Extrae tabla/vista; usa datos demo si Supabase no está disponible."""
        if _self._demo_mode:
            return pd.DataFrame()          # session_state ya fue hidratado en app.py

        try:
            response = _self.client.table(table_name).select("*").execute()
            if not response.data:
                return pd.DataFrame()
            df = pd.DataFrame(response.data)
            _self._normalize(df)
            return df
        except Exception as e:
            st.warning(f"⚠️ Conexión remota no disponible — modo demo activado.")
            return pd.DataFrame()

    @staticmethod
    def _normalize(df: pd.DataFrame):
        """Convierte valores estandarizados (Z-Score) a rangos reales de negocio."""
        if "monetary"        in df.columns: df["monetary"]        = (df["monetary"].abs()        * 1500) + 100
        if "avg_monetary"    in df.columns: df["avg_monetary"]    = (df["avg_monetary"].abs()    * 1500) + 100
        if "lifetime_value"  in df.columns: df["lifetime_value"]  = (df["lifetime_value"].abs()  * 1500) + 100
        if "recency"         in df.columns: df["recency"]         = (df["recency"].abs()         * 30).astype(int) + 1
        if "frequency"       in df.columns: df["frequency"]       = (df["frequency"].abs()       * 10).astype(int) + 1
        if "rfm_score"       in df.columns: df["rfm_score"]       = (df["rfm_score"].abs()       * 5).astype(int) + 1
        if "churn_probability" in df.columns:
            df["churn_probability"] = df["churn_probability"].apply(lambda x: x if x > 1 else x * 100)
        if "churn_risk_pct"  in df.columns:
            df["churn_risk_pct"]    = df["churn_risk_pct"].apply(lambda x: x if x > 1 else x * 100)


def get_repository() -> SupabaseRepository:
    url = ""
    key = ()
    return SupabaseRepository(url, key).connect()
