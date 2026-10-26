# 🏆 Estrategias de Retención — Análisis de Churn E-Commerce
## Insights de Negocio Basados en el Modelo Predictivo

> **Dataset:** Online Retail II (UCI) | ~4,300 clientes únicos  
> **Criterio de Churn:** 90 días de inactividad comercial  
> **Modelo Champion:** XGBoost con manejo de desbalance de clases  
> **Features clave según SHAP:** Recency > Monetary > Frequency > AvgTicket

---

## 🔍 Hallazgos Principales del Análisis

### 1. La Recency es el predictor más poderoso
El análisis SHAP revela que **Recency** (días desde la última compra) explica la mayor parte del riesgo de churn. Un cliente que no compra en más de 60 días tiene una probabilidad de abandono 3x mayor que uno activo en los últimos 30 días.

### 2. Existe un "punto de no retorno" alrededor de los 120 días
El análisis del ThresholdAnalyzer muestra que a partir de los 120 días de inactividad, la tasa de conversión de campañas de reactivación cae drásticamente. La intervención óptima es entre los **45 y 90 días** de inactividad.

### 3. Los clientes de alto valor (VIP) tienen patrones de churn distintos
Los clientes VIP (RFM_Score ≥ 9) que entran en riesgo suelen tener una caída gradual en frequency, no en recency. Esto sugiere que compran menos veces, pero siguen activos — lo que los hace **difíciles de detectar sin el modelo ML**.

### 4. El ticket promedio predice lealtad
Clientes con `AvgTicket` > £50 tienen un 40% menos de probabilidad de churn que clientes de bajo ticket. **La calidad de la relación importa más que la frecuencia**.

---

## 🎯 Estrategias por Segmento

### 🔴 Riesgo Muy Alto (ChurnProbability ≥ 70%)
**Perfil:** Cliente inactivo >90 días, Recency > Frequency desbalanceado.  
**Ventana de acción:** Máximo 2 semanas antes de que el costo de reactivación sea mayor al LTV.

| Acción | Canal | Timing | KPI de Éxito |
|--------|-------|--------|--------------|
| **Cupón de reactivación 25-30%** | Email personalizado | Inmediato | Tasa de conversión >5% |
| **Encuesta de salida** | Email + SMS | +48h sin respuesta | Completions >20% |
| **Recordatorio de carrito abandonado** | Email + Push | Si tiene carrito | CTR >15% |
| **Oferta "Te extrañamos"** | Email | +7 días sin acción | Conversión >3% |

### 🟡 Riesgo Medio (ChurnProbability 40%–70%)
**Perfil:** Cliente que reduce frecuencia, tickets menores que el promedio histórico.  
**Ventana de acción:** 3-4 semanas.

| Acción | Canal | Objetivo |
|--------|-------|---------|
| **Newsletter personalizada** con recomendaciones basadas en historial | Email | Mantener engagement |
| **Puntos de fidelización dobles** en próxima compra | App / Email | Incrementar Frequency |
| **Cross-sell automatizado** de productos complementarios | Web + Email | Aumentar AvgTicket |

### 🟢 Estable — Riesgo Bajo (ChurnProbability < 40%)
**Perfil:** Compradores activos recientes.  
**Objetivo:** Maximizar LTV y convertirlos en VIP.

| Acción | Objetivo |
|--------|---------|
| **Programa de referidos** (crédito por referido) | Adquisición de nuevos clientes |
| **Upgrade a membership premium** | Aumentar Monetary |
| **Acceso anticipado** a nuevos productos | Fortalecer lealtad |

### 💎 VIP / Champion en Riesgo (RFM_Score ≥ 9 AND RiskSegment ≠ 'Estable')
**Perfil:** Alto valor histórico pero señales de debilitamiento de relación.  
**Criticidad:** MÁXIMA — pérdida de un VIP equivale a 10+ clientes regulares.

| Acción | Racional |
|--------|---------|
| **Contacto directo del equipo de cuenta** (email/llamada personalizada) | Relación humana, no automatizada |
| **Acceso a ventas privadas / eventos exclusivos** | Exclusividad y reconocimiento |
| **Gift de lealtad** (envío gratuito permanente, puntos bonificados) | Refuerzo positivo del vínculo |
| **Gestor de cuenta asignado** para clientes con LTV > £2,000 | Retención proactiva |

---

## 📊 Métricas de Negocio a Monitorear en Power BI

| Métrica | Definición | Frecuencia | Alerta |
|---------|-----------|-----------|--------|
| **Churn Rate Mensual** | % de clientes que pasan a inactivos | Mensual | > 5% variación |
| **Exposición Monetaria** | Suma del Monetary de clientes en Riesgo Alto | Semanal | > £50K |
| **VIPs en Riesgo** | Count VIP + RiskSegment ≠ Estable | Semanal | > 10 clientes |
| **Tasa de Reactivación** | % de Riesgo Alto que compran tras campaña | Mensual | < 3% = revisar campaña |
| **LTV Proyectado** | Monetary medio × Frequency media × vida útil | Trimestral | Trend decreciente |
| **Model Recall** | % de churners reales detectados | Por pipeline run | < 0.80 → re-entrenar |

---

## 💡 Recomendaciones Técnicas

1. **Re-entrenar el modelo mensualmente** con los últimos 12 meses de datos.
2. **Monitorear data drift** con `monitoring/drift_detector.py` tras cada lote de datos nuevos.
3. **A/B Testing** en las campañas de reactivación: medir qué descuento (20% vs 30%) maximiza ROI.
4. **Actualizar el umbral de Churn** (90 días) tras cada temporada alta — el comportamiento post-Navidad cambia la distribución de Recency.

---

*Documento generado por el pipeline de Churn Prediction. Actualizar tras cada ejecución del modelo.*  
*Última actualización: Ver `reports/metrics.md` para fecha del último run.*