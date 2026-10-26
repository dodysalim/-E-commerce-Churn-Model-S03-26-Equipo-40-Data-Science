import os
import sys
import pandas as pd

# Añadir el directorio raíz al path para importar desde src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preprocessing import clean_and_feature_engineering, scale_features
from src.churn_label import define_churn
from src.model import train_and_evaluate, interpret_model, save_model
from src.segmentation import segment_customers_by_risk, rfm_segmentation
from src.export_to_supabase import sync_results

def run_full_pipeline():
    print("🚀 Iniciando Pipeline de Predicción de Churn...")
    
    # 1. Carga de datos
    data_path = 'data/raw/online_retail_II.csv'
    if not os.path.exists(data_path):
        print(f"❌ Error: No se encontró el dataset en {data_path}")
        return
    
    print("📥 Cargando datos...")
    # Cargamos solo las columnas necesarias para ahorrar memoria
    cols = ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID', 'Country']
    raw_df = pd.read_csv(data_path, usecols=cols)
    
    # 2. Preprocesamiento y RFM
    print("🛠️ Limpiando datos y calculando métricas RFM...")
    rfm_df = clean_and_feature_engineering(raw_df)
    
    # 3. Etiquetado de Churn
    print("🏷️ Definiendo etiquetas de Churn (90 días)...")
    df_with_label = define_churn(rfm_df)
    
    # Guardar temporalmente el procesado
    os.makedirs('data/processed', exist_ok=True)
    df_with_label.to_csv('data/processed/rfm_with_churn.csv', index=False)
    
    # 4. Entrenamiento de Modelos
    print("🤖 Entrenando y evaluando modelos predictivos...")
    best_model, name, metrics, X_train, X_test, y_test = train_and_evaluate(df_with_label)
    
    # Guardar modelo
    save_model(best_model, name)
    
    # 5. Segmentación y Probabilidades
    print("📊 Generando segmentación de riesgo y niveles de cliente...")
    features = ['Recency', 'Frequency', 'Monetary']
    final_df = segment_customers_by_risk(df_with_label, best_model, features)
    final_df = rfm_segmentation(final_df)
    
    # Guardar resultados finales localmente
    final_df.to_csv('data/processed/final_customer_results.csv', index=False)
    print(f"✅ Resultados guardados en data/processed/final_customer_results.csv")
    
    # 6. Exportación a Supabase
    print("☁️ Sincronizando resultados con Supabase...")
    try:
        sync_results(final_df)
    except Exception as e:
        print(f"⚠️ Error al exportar a Supabase: {e}. Asegúrate de tener configurado el archivo .env.")

    print("\n✨ Proceso completado con éxito.")

if __name__ == "__main__":
    run_full_pipeline()