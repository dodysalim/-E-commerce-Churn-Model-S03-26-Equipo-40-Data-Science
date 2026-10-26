import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import datetime as dt

def clean_and_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza la limpieza inicial y genera las características RFM.
    """
    # 1. Limpieza Inicial
    # Eliminar registros sin ID de cliente
    df = df[df['Customer ID'].notnull()].copy()
    
    # Asegurar tipos de datos
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Customer ID'] = df['Customer ID'].astype(str)
    
    # Eliminar cancelaciones (Invoices que empiezan con 'C')
    df = df[~df['Invoice'].str.contains('C', na=False)]
    
    # 2. Ingeniería de Características
    # Calcular Monto Total por línea
    df['TotalSum'] = df['Quantity'] * df['Price']
    
    # Definir fecha de referencia (snapshot) como el día después de la última compra
    snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)
    
    # Agrupar por Cliente para obtener métricas RFM
    rfm = df.groupby('Customer ID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days, # Recency
        'Invoice': 'nunique',                                  # Frequency
        'TotalSum': 'sum'                                      # Monetary
    })
    
    # Renombrar columnas
    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'Invoice': 'Frequency',
        'TotalSum': 'Monetary'
    }, inplace=True)
    
    # Reset index para tener Customer ID como columna
    rfm = rfm.reset_index()
    
    # 3. Tratamiento de Outliers (opcional but recommended for E-commerce)
    # Aquí podríamos aplicar un clip o log transform para Monetary y Frequency
    
    return rfm

def scale_features(df: pd.DataFrame, features: list) -> pd.DataFrame:
    """
    Aplica escalamiento estándar a las características seleccionadas.
    """
    scaler = StandardScaler()
    df_scaled = df.copy()
    df_scaled[features] = scaler.fit_transform(df[features])
    return df_scaled, scaler