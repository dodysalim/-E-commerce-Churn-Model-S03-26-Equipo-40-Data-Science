import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import recall_score, f1_score, roc_auc_score, accuracy_score
import shap
import joblib 
import os

def train_and_evaluate(df: pd.DataFrame, target: str = 'CHURN'):
    """
    Entrena varios modelos y devuelve el mejor basado en Recall.
    """
    # Excluimos ID de cliente y target de las features
    X = df.drop(columns=[target, 'Customer ID'])
    y = df[target]
    
    # Split con estratificación dado que el churn suele ser desbalanceado
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1),
        'LogisticRegression': LogisticRegression(max_iter=1000, solver='lbfgs', random_state=42),
        'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    }
    
    results = {}
    best_recall = 0
    best_model = None
    best_model_name = ""
    
    print("\n--- Model Evaluation (Target: Recall) ---")
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
        acc = accuracy_score(y_test, y_pred)
        
        results[name] = {
            'Recall': recall, 
            'F1': f1, 
            'AUC': auc,
            'Accuracy': acc
        }
        print(f"{name} -> Recall: {recall:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}, Acc: {acc:.4f}")
        
        if recall > best_recall:
            best_recall = recall
            best_model = model
            best_model_name = name
            
    print(f"\nModel seleccionado: {best_model_name} con Recall de {best_recall:.4f}")
    
    return best_model, best_model_name, results, X_train, X_test, y_test

def interpret_model(model, X_train, model_name):
    """
    Genera valores SHAP para la interpretabilidad del modelo seleccionado.
    """
    print(f"\nGenerando interpretabilidad SHAP para {model_name}...")
    
    # Para modelos basados en árboles
    if model_name in ['RandomForest', 'XGBoost']:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_train)
        return explainer, shap_values
    else:
        # Linear models use LinearExplainer
        explainer = shap.LinearExplainer(model, X_train)
        shap_values = explainer.shap_values(X_train)
        return explainer, shap_values

def save_model(model, name, path='models/'):
    """
    Guarda el modelo entrenado y los resultados en disco.
    """
    if not os.path.exists(path):
        os.makedirs(path)
    
    filename = os.path.join(path, f"{name.lower()}_churn_model.pkl")
    joblib.dump(model, filename)
    print(f"Modelo guardado exitosamente en: {filename}")
    return filename