# 📊 Métricas del Modelo de Predicción de Churn

> **Modelo Seleccionado:** RandomForest  
> **Criterio de selección:** Maximizar **Recall** (minimizar falsos negativos)  

## 🏆 Comparativa de Modelos (Validación Cruzada — 5 Folds)

| Modelo | Recall (CV) ± Std | F1 (CV) | AUC (CV) | Accuracy (CV) |
|--------|-------------------|---------|----------|---------------|
| RandomForest | 1.0000 ± 0.000 | 1.0000 | 1.0000 | 1.0000 |
| LogisticRegression | 0.9728 ± 0.003 | 0.9862 | 1.0000 | 0.9862 |
| XGBoost | 0.9987 ± 0.001 | 0.9992 | 1.0000 | 0.9991 |

## ✅ Métricas Finales (Test Set — 20% holdout)

| Métrica | Valor |
|---------|-------|
| **Recall** *(prioritaria)* | **1.0000** |
| F1 Score | 1.0000 |
| ROC-AUC | 1.0000 |
| Accuracy | 1.0000 |

## 🔍 Interpretación

- Un Recall de **100.0%** significa que el modelo detecta correctamente ese porcentaje de clientes que abandonarán.
- Los **falsos negativos** (clientes en riesgo no detectados) son el error más costoso en churn.
- La curva Precision-Recall permite ajustar el umbral de decisión según el presupuesto de retención.