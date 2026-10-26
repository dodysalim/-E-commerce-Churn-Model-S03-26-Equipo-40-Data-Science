# 📊 Guía de Conexión Supabase → Power BI

## Objetivo
Conectar Power BI Desktop directamente a las tablas y vistas de Supabase
para construir el dashboard de Churn Prediction en tiempo real.

---

## Pre-requisitos

- [ ] Power BI Desktop instalado (versión reciente)
- [ ] Acceso a tu proyecto Supabase (URL y credenciales)
- [ ] Pipeline ejecutado al menos una vez (`make run`)
- [ ] Tablas desplegadas en Supabase (`make db-deploy`)

---

## Paso 1: Obtener Credenciales de Supabase

1. Ve a tu [Supabase Dashboard](https://app.supabase.com)
2. Selecciona tu proyecto
3. En el menú izquierdo: **Project Settings → Database**
4. Copia los datos de **Connection String → URI**:
   ```
   postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```

---

## Paso 2: Conectar Power BI a PostgreSQL

1. Abre **Power BI Desktop**
2. Click en **"Obtener datos"** → **"Más..."**
3. Busca **"PostgreSQL"** y selecciónalo
4. Introduce los datos de conexión:
   | Campo | Valor |
   |-------|-------|
   | Servidor | `db.[PROJECT_REF].supabase.co` |
   | Base de datos | `postgres` |
   | Puerto | `5432` |
5. Click en **"Aceptar"**
6. En el diálogo de autenticación:
   - Usuario: `postgres`
   - Contraseña: tu DATABASE PASSWORD de Supabase

---

## Paso 3: Seleccionar Tablas y Vistas

En el **Navegador** de Power BI, selecciona:

| Nombre | Tipo | Uso en Dashboard |
|--------|------|-----------------|
| `customer_churn_results` | Tabla | Tabla principal con todos los clientes |
| `v_executive_churn_summary` | Vista | KPI cards del banner principal |
| `v_value_risk_matrix` | Vista | Gráfico de dispersión Valor vs Riesgo |
| `v_vips_at_risk` | Vista | Tabla de clientes VIP en peligro |
| `v_top_priority_customers` | Vista | Lista de acción inmediata |
| `v_customer_distribution` | Vista | Gráfico de barras apiladas |
| `v_global_metrics` | Vista | Métricas globales del modelo |

---

## Paso 4: Medidas DAX Recomendadas

Una vez cargados los datos, crea estas medidas en Power BI:

```dax
// Tasa de Churn Global
Churn Rate % = 
    DIVIDE(
        COUNTROWS(FILTER(customer_churn_results, customer_churn_results[churn] = 1)),
        COUNTROWS(customer_churn_results)
    ) * 100

// Exposición Monetaria Total (Riesgo Muy Alto)
Exposicion Alto Riesgo = 
    CALCULATE(
        SUM(customer_churn_results[monetary]),
        customer_churn_results[risk_segment] = "Riesgo Muy Alto"
    )

// Clientes VIP en Riesgo
VIPs en Riesgo = 
    CALCULATE(
        COUNTROWS(customer_churn_results),
        customer_churn_results[customer_level] = "VIP / Champion",
        customer_churn_results[risk_segment] IN {"Riesgo Muy Alto", "Riesgo Medio"}
    )

// Recall del Modelo (estático - actualizar manualmente)
Model Recall = 0.87  -- Actualizar con el valor real de reports/metrics.md
```

---

## Paso 5: Actualización Automática de Datos

Para que Power BI se actualice automáticamente cuando el pipeline re-ejecute:

1. Publica el report en **Power BI Service**
2. Configura una **Gateway de datos** (para conexión PostgreSQL on-cloud)
3. En Power BI Service: **"Configurar actualización programada"**
   - Frecuencia recomendada: Diaria o Semanal según el pipeline

---

## Estructura Recomendada del Dashboard

```
📊 PANEL PRINCIPAL
├── 🎯 Banner KPIs (v_global_metrics)
│   ├── Tasa de Churn Total: X%
│   ├── Clientes en Riesgo Alto: N
│   └── Exposición Monetaria: £XX,XXX
│
├── 📈 Distribución de Riesgo (v_executive_churn_summary)
│   └── Gráfico de donut/barras por RiskSegment
│
├── 💎 Matriz Valor vs Riesgo (v_value_risk_matrix)
│   └── Scatter: Monetary (eje Y) vs ChurnProbability (eje X)
│
├── 🚨 VIPs en Peligro (v_vips_at_risk)
│   └── Tabla filtrada con acciones de retención
│
└── 📋 Top 50 Clientes Prioritarios (v_top_priority_customers)
    └── Tabla ordenada por pérdida esperada
```
