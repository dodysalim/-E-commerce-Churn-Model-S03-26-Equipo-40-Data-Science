import pandas as pd

def define_churn(df: pd.DataFrame, threshold_days: int = 90) -> pd.DataFrame:
    """
    Define la etiqueta de Churn basada en la columna 'Recency'.
    Si Recency > threshold_days, CHURN = 1, de lo contrario 0.
    """
    if 'Recency' not in df.columns:
        raise ValueError("La columna 'Recency' es necesaria para definir el Churn.")
    
    df['CHURN'] = df['Recency'].apply(lambda x: 1 if x > threshold_days else 0)
    
    # Análisis rápido de balance de clases
    churn_rate = df['CHURN'].mean() * 100
    print(f"Tasa de Churn detectedda: {churn_rate:.2f}%")
    
    return df