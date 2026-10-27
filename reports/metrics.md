# 📊 Métricas del Modelo de Predicción de Churn

> **Modelo Seleccionado:** RandomForest  
> **Criterio de selección:** Maximizar **Recall** (minimizar falsos negativos)  

## 🏆 Comparativa de Modelos (Validación Cruzada — 5 Folds)

| Modelo | Recall (CV) ± Std | F1 (CV) | AUC (CV) | Accuracy (CV) |
|--------|-------------------|---------|----------|---------------|
| RandomForest | 0.7589 ± 0.014 | 0.7603 | 0.7962 | 0.7283 |
| LogisticRegression | 0.7134 ± 0.017 | 0.7433 | 0.7915 | 0.7203 |
| XGBoost | 0.7543 ± 0.018 | 0.7505 | 0.7842 | 0.7153 |

## ✅ Métricas Finales (Test Set — 20% holdout)

| Métrica | Valor |
|---------|-------|
| **Recall** *(prioritaria)* | **0.7800** |
| F1 Score | 0.7710 |
| ROC-AUC | 0.7946 |
| Accuracy | 0.7367 |

## 🔍 Interpretación

- Un Recall de **78.0%** significa que el modelo detecta correctamente ese porcentaje de clientes que abandonarán.
- Los **falsos negativos** (clientes en riesgo no detectados) son el error más costoso en churn.
- La curva Precision-Recall permite ajustar el umbral de decisión según el presupuesto de retención.