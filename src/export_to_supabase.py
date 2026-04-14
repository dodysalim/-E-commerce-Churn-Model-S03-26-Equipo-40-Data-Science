import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """
    Inicializa el cliente de Supabase usando variables de entorno.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar presentes en el archivo .env")
    return create_client(url, key)

def export_dataframe_to_supabase(df: pd.DataFrame, table_name: str):
    """
    Exporta un DataFrame a una tabla específica en Supabase.
    """
    supabase = get_supabase_client()
    
    # Limpiar nulos para evitar errores en Postgres
    df = df.fillna(0)
    
    # Convertir DataFrame a lista de diccionarios
    data = df.to_dict(orient='records')
    
    print(f"Exportando {len(data)} registros a la tabla '{table_name}' en Supabase...")
    
    # Supabase maneja inserts en batches de forma nativa con la librería
    try:
        # En Supabase es más eficiente insertar en chunks si el dataset es muy grande
        chunk_size = 500
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            response = supabase.table(table_name).insert(chunk).execute()
        
        print("Exportación completada exitosamente.")
    except Exception as e:
        print(f"Error durante la exportación: {e}")

def sync_results(final_df: pd.DataFrame):
    """
    Sincroniza los resultados finales (Churn + Riesgo + RFM) a Supabase.
    """
    # Seleccionamos las columnas relevantes para el dashboard de Power BI
    cols_to_export = [
        'Customer ID', 'Recency', 'Frequency', 'Monetary', 
        'CHURN', 'ChurnProbability', 'RiskSegment', 'CustomerLevel'
    ]
    
    chunk_to_db = final_df[cols_to_export].copy()
    export_dataframe_to_supabase(chunk_to_db, 'customer_churn_results')