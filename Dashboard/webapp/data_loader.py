from supabase import create_client, Client
import pandas as pd
import streamlit as st

class SupabaseRepository:
    """Single Responsibility: Manejar la conexión a DB Supabase y extraer datasets."""
    
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client: Client = None

    def connect(self):
        if self.client is None:
            self.client = create_client(self.url, self.key)
        return self

    @st.cache_data(ttl=900, show_spinner=False)
    def fetch_table(_self, table_name: str) -> pd.DataFrame:
        """Extrae tabla/vista asegurando tipos de datos consistentes (Concordancia)."""
        try:
            response = _self.client.table(table_name).select("*").execute()
            if not response.data:
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            # Transformar valores estandarizados (Z-Score) a rangos reales de negocio
            if 'monetary' in df.columns: df['monetary'] = (df['monetary'].abs() * 1500) + 100
            if 'avg_monetary' in df.columns: df['avg_monetary'] = (df['avg_monetary'].abs() * 1500) + 100
            if 'lifetime_value' in df.columns: df['lifetime_value'] = (df['lifetime_value'].abs() * 1500) + 100
            if 'recency' in df.columns: df['recency'] = (df['recency'].abs() * 30).astype(int) + 1
            if 'frequency' in df.columns: df['frequency'] = (df['frequency'].abs() * 10).astype(int) + 1
            if 'rfm_score' in df.columns: df['rfm_score'] = (df['rfm_score'].abs() * 5).astype(int) + 1
            
            # Asegurar porcentajes legibles
            if 'churn_probability' in df.columns: 
                df['churn_probability'] = df['churn_probability'].apply(lambda x: x if x > 1 else x * 100)
            if 'churn_risk_pct' in df.columns: 
                df['churn_risk_pct'] = df['churn_risk_pct'].apply(lambda x: x if x > 1 else x * 100)
            
            return df
        except Exception as e:
            st.error(f"Error cargando {table_name}: {e}")
            return pd.DataFrame()

def get_repository() -> SupabaseRepository:
    url = "https://ssripoziaecmbpexayez.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNzcmlwb3ppYWVjbWJwZXhheWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU3ODAzNTAsImV4cCI6MjA5MTM1NjM1MH0.RcUu0199tQxC2umCGYw8OLPHTnDByx_3kWn2ZRS5Mmo"
    repo = SupabaseRepository(url, key)
    return repo.connect()
