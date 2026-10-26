# 📊 Reporte Ejecutivo — Churn Prediction E-Commerce
> **Generado:** 2026-04-10 13:44  
> **Equipo:** No Country — Equipo 40  
> **Dataset:** Online Retail II (UCI ML Repository)

---

## 🎯 KPIs Principales

| Indicador | Valor | Estado |
|-----------|-------|--------|
| Total de clientes analizados | 5,878 | — |
| Tasa de churn global | 50.9% | 🔴 Alta |
| Clientes en Riesgo Muy Alto | 2,989 (50.9%) | 🔴 Acción inmediata |
| Exposición monetaria (Alto) | £3,301,723 | 🔴 Crítico |
| Clientes VIP en riesgo | 319 | 🔴 Urgente |

## 🎯 Acciones Inmediatas Recomendadas

1. **Contactar los 50 clientes de mayor prioridad** esta semana  
   → ver `data/exports/top_priority_customers.csv`

2. **Proteger los 319 clientes VIP en riesgo** con contacto personalizado  
   → ver `data/exports/vip_at_risk.csv`

3. **Conectar el dashboard en Power BI**  
   → seguir `docs/powerbi_setup_guide.md`

## 📁 Archivos Generados

| Archivo | Uso |
|---------|-----|
| `data/exports/customer_churn_results.csv` | Tabla completa → Power BI |
| `data/exports/vip_at_risk.csv` | VIPs en peligro → Priority team |
| `data/exports/top_priority_customers.csv` | Lista de contacto → Marketing |
| `reports/executive_dashboard.png` | Dashboard visual → Presentación |
| `reports/metrics.md` | Métricas del modelo → Data Science |

---
*Para estrategias detalladas por segmento, ver: `reports/insights.md`*  
*Para ejecutar el pipeline completo: `python pipelines/run_full_pipeline.py`*
