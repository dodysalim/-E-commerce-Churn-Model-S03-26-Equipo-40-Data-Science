import os
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client, Client
import pandas as pd
import numpy as np
import streamlit as st

# ──────────────────────────────────────────────
#  DEMO DATA — se activa si Supabase no responde
# ──────────────────────────────────────────────
def _generate_demo_data():
    """Genera datos realistas para demostración offline."""
    rng = np.random.default_rng(42)
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
        "customer_level": rng.choice(levels, N, p=[0.06, 0.15, 0.35, 0.28, 0.16]),
        "risk_segment":   rng.choice(segments, N, p=[0.25, 0.45, 0.30]),
        "recency":        rng.integers(1, 180, N),
        "frequency":      rng.integers(1, 50, N),
        "monetary":       rng.lognormal(7.5, 1.2, N),
        "rfm_score":      rng.integers(1, 6, N),
        "churn_probability": rng.beta(2, 5, N) * 100,
        "lifetime_value": rng.lognormal(8.0, 1.1, N),
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
        if not self.url or not self.key:
            self._demo_mode = True
            return self
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
        """Preserve business units; only probability [0,1] is displayed as percent.

        SQL views already return *_pct percentages. They must not be multiplied
        again. A scaler cannot be inverted without its fitted parameters.
        """
        if "churn_probability" in df.columns:
            values = pd.to_numeric(df["churn_probability"], errors="raise")
            if values.dropna().between(0, 1).all():
                df["churn_probability"] = values * 100
            else:
                raise ValueError("churn_probability must be in [0, 1] in the SQL source")


def get_repository() -> SupabaseRepository:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    try:
        url = st.secrets.get("SUPABASE_URL", url)
        key = st.secrets.get("SUPABASE_KEY", key)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        pass
    return SupabaseRepository(url, key).connect()
