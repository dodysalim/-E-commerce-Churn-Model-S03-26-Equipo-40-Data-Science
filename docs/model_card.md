# 🧠 Model Card — E-Commerce Churn Prediction Model
## No Country — Equipo 40

> **Propósito de este documento:** Transparencia sobre las capacidades, limitaciones, sesgos y contexto de uso del modelo de predicción de churn. Siguiendo las mejores prácticas de ML responsable (Google, 2019).

---

## 📋 Información General

| Campo | Detalle |
|-------|---------|
| **Nombre del modelo** | E-Commerce Churn Classifier |
| **Versión** | 2.0 |
| **Tipo** | Clasificación binaria supervisada |
| **Algoritmo primario** | XGBoost / Random Forest (seleccionado por Recall) |
| **Dataset de entrenamiento** | Online Retail II — UCI ML Repository |
| **Fecha de entrenamiento** | Ver `models/champion/champion_info.json` |
| **Autor** | No Country — Equipo 40 |
| **Contacto** | Ver `pyproject.toml` |

---

## 🎯 Uso Previsto

### ¿Para qué está diseñado?

El modelo está diseñado para **identificar proactivamente clientes en riesgo de abandono** en un entorno de e-commerce de retail online. Los outputs del modelo alimentan:

1. **Campañas de retención automatizadas** (email, descuentos, contacto VIP)
2. **Dashboard ejecutivo de Power BI** con KPIs de churn en tiempo real
3. **Priorización del equipo de marketing** (top N clientes a contactar primero)

### ¿Quiénes son los usuarios directos?

- Equipos de Marketing y CRM
- Analistas de datos y científicos de datos
- Directores de operaciones y negocio

### ¿Qué NO debe usarse para?

> [!CAUTION]
> - **Decisiones legales o discriminatorias** contra clientes
> - **Segmentar clientes por datos demográficos** (el modelo no usa ni edad, ni género, ni raza)
> - **Inferir comportamiento individual futuro** con 100% de certeza — es un sistema probabilístico

---

## 📊 Métricas de Rendimiento

| Métrica | Valor | Significado |
|---------|-------|-------------|
| **Recall** *(prioritaria)* | ~0.87+ | El modelo detecta el 87%+ de churners reales |
| **F1-Score** | ~0.82+ | Balance entre precisión y recall |
| **ROC-AUC** | ~0.91+ | Discriminación general del modelo |
| **Accuracy** | ~0.85+ | Corrección global de predicciones |

> [!NOTE]
> Los valores exactos actualizados se encuentran en `reports/metrics.md` tras cada ejecución del pipeline.

### ¿Por qué priorizamos Recall sobre Accuracy?

En churn prediction, el **falso negativo** (no detectar un churner real) es más costoso que el **falso positivo** (contactar a un cliente que no iba a abandonar). Contactar de más es barato; perder un cliente VIP es caro.

---

## 🗃️ Dataset

| Característica | Detalle |
|----------------|---------|
| **Fuente** | [UCI ML Repository — Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) |
| **Cobertura temporal** | Dic 2009 – Dic 2011 |
| **País principal** | United Kingdom (~90% de transacciones) |
| **Clientes únicos** | ~4,300 (tras limpieza) |
| **Transacciones** | ~1,000,000 (raw) → ~750,000 (post-limpieza) |
| **Target** | `CHURN = 1` si inactivo > 90 días |
| **Datos sensibles** | No contiene datos demográficos, únicamente comportamentales (RFM) |

### Limitaciones del dataset

- Solo incluye transacciones UK-centric — las predicciones para mercados internacionales pueden ser menos precisas
- El período temporal (2009-2011) puede no reflejar comportamientos post-pandemia
- ~25% de transacciones sin `Customer ID` son descartadas — posible sesgo de selección hacia clientes registrados

---

## ⚙️ Features Utilizadas

| Feature | Tipo | Descripción | Importancia SHAP (aprox.) |
|---------|------|-------------|--------------------------|
| `Recency` | Numérica | Días desde última compra | ⭐⭐⭐⭐⭐ (más alta) |
| `Frequency` | Numérica | Número de facturas únicas | ⭐⭐⭐⭐ |
| `Monetary` | Numérica | Gasto total histórico (£) | ⭐⭐⭐⭐ |
| `AvgTicket` | Derivada | Ticket promedio por factura | ⭐⭐⭐ |
| `DaysBetweenPurchases` | Derivada | Promedio de días entre compras | ⭐⭐⭐ |
| `MonetaryStdDev` | Derivada | Variabilidad del gasto | ⭐⭐ |
| `UniqueProducts` | Derivada | Diversidad de productos comprados | ⭐⭐ |
| `PeakHourBuyer` | Derivada | Proporción de compras en hora pico | ⭐ |

### ¿Qué NO se usa?

- Datos demográficos (edad, género, ubicación)
- Datos de marketing previo (correos abiertos, clicks)
- Información de devoluciones (correlacionada con cancelaciones, ya filtradas)

---

## ⚠️ Limitaciones y Riesgos Conocidos

### 1. Desbalance de Clases
El dataset puede presentar desbalance (churn minoritario). Se mitiga con:
- `class_weight='balanced'` en Random Forest y Logistic Regression
- `scale_pos_weight` dinámico en XGBoost

### 2. Data Drift
El comportamiento de compra cambia estacionalmente (navidad, rebajas). El modelo puede degradarse si no se re-entrena periódicamente.

> [!WARNING]
> **Monitorear con:** `python monitoring/drift_detector.py`  
> **Frecuencia recomendada:** Mensual o tras eventos de temporada alta

### 3. Representatividad Geográfica
El dataset está sesgado hacia clientes del Reino Unido. Si el negocio se expande a otros mercados, re-entrenar con datos locales.

### 4. Umbral de 90 Días
El umbral de inactividad fue seleccionado analíticamente para este dataset. Puede no ser óptimo para otros segmentos de negocio (suscripciones, B2B, luxury goods).

---

## 🔄 Ciclo de Vida del Modelo

| Evento | Acción recomendada |
|--------|-------------------|
| Cada mes | Ejecutar `make run` para actualizar predicciones |
| Si Recall cae < 0.80 | Re-entrenar con `make train` |
| Si drift detectado en >3 features | Re-entrenar urgente |
| Nuevo segmento de negocio | Re-entrenar con datos nuevos |
| Cambios en el catálogo de productos | Revisar umbral de Recency |

---

## 📜 Consideraciones Éticas

- **Transparencia:** Los stakeholders deben saber que las acciones de marketing están guiadas por un modelo predictivo
- **Apelación:** Los clientes clasificados como "Riesgo Muy Alto" NO deben ser penalizados; la acción es de retención positiva
- **Revisión humana:** Decisiones de alto impacto (cancelación de contratos VIP) deben ser revisadas por un humano
- **No discriminación:** El modelo no debe usarse para excluir clientes de ningún servicio

---

*Documento generado siguiendo el estándar [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) (Mitchell et al., 2019).*
