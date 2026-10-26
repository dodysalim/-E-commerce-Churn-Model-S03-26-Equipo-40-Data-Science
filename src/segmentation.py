import pandas as pd
import numpy as np

def segment_customers_by_risk(df: pd.DataFrame, model, features: list) -> pd.DataFrame:
    """
    Asigna una probabilidad de Churn y segmenta a los clientes en niveles de riesgo.
    """
    # Predecir probabilidades de la clase 1 (Churn)
    probs = model.predict_proba(df[features])[:, 1]
    df['ChurnProbability'] = probs
    
    # Definir Segmentos de Riesgo
    def categorize_risk(prob):
        if prob >= 0.7:
            return 'Riesgo Muy Alto'
        elif prob >= 0.4:
            return 'Riesgo Medio'
        else:
            return 'Estable (Riesgo Bajo)'

    df['RiskSegment'] = df['ChurnProbability'].apply(categorize_risk)
    
    return df

def rfm_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Segmentación RFM tradicional basada en cuartiles.
    """
    # Crear puntajes 1-4 (cuartiles)
    # Recency: menor es mejor (4)
    df['R_Score'] = pd.qcut(df['Recency'], 4, labels=[4, 3, 2, 1])
    # Frequency: mayor es mejor (4)
    df['F_Score'] = pd.qcut(df['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    # Monetary: mayor es mejor (4)
    df['M_Score'] = pd.qcut(df['Monetary'], 4, labels=[1, 2, 3, 4])
    
    # Combinar puntajes
    df['RFM_Group'] = df['R_Score'].astype(str) + df['F_Score'].astype(str) + df['M_Score'].astype(str)
    df['RFM_Score'] = df[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)
    
    def rfm_level(score):
        if score >= 9:
            return 'VIP / Champion'
        elif score >= 6:
            return 'Leales / Prometedores'
        else:
            return 'En Riesgo / Perdidos'

    df['CustomerLevel'] = df['RFM_Score'].apply(rfm_level)
    
    return df