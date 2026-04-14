# 📖 Diccionario de Datos — Online Retail II Dataset

> **Fuente:** UCI Machine Learning Repository  
> **URL:** https://archive.ics.uci.edu/dataset/502/online+retail+ii  
> **Cobertura:** Transacciones de una tienda de retail online, UK, 2009–2011  
> **Archivo:** `data/raw/online_retail_II.csv`

---

## Columnas del Dataset Raw

| Columna | Tipo | Descripción | Valores / Formato |
|---------|------|-------------|-------------------|
| `Invoice` | string | Número de factura único por transacción. Si empieza con **'C'**, es una cancelación. | Ej: `536365`, `C536379` |
| `StockCode` | string | Código único del producto. | Ej: `85123A`, `71053` |
| `Description` | string | Nombre del producto. Puede ser nulo. | Texto libre |
| `Quantity` | integer | Número de unidades por transacción. Valores negativos = cancelaciones o ajustes. | Ej: `6`, `-1`, `12` |
| `InvoiceDate` | datetime | Fecha y hora de la transacción. | `YYYY-MM-DD HH:MM:SS` |
| `Price` | float | Precio unitario en libras esterlinas (£). | Ej: `2.55`, `0.85` |
| `Customer ID` | string | Identificador único del cliente. Puede ser nulo (~25% del dataset). | Ej: `17850`, `15311.0` |
| `Country` | string | País del cliente. Mayoría UK. | Ej: `United Kingdom`, `France` |

---

## Columnas Generadas por el Pipeline

### Capa Intermedia (`data/interim/`)

| Columna | Origen | Descripción |
|---------|--------|-------------|
| `TotalSum` | `Quantity * Price` | Valor total de la línea de transacción en £ |

### Metrics RFM (`data/interim/rfm_raw.parquet`)

| Columna | Descripción | Cómo se calcula |
|---------|-------------|-----------------|
| `Recency` | Días desde la última compra del cliente | `(snapshot_date - max(InvoiceDate)).days` |
| `Frequency` | Número de facturas únicas del cliente | `nunique(Invoice)` por cliente |
| `Monetary` | Gasto total histórico del cliente en £ | `sum(TotalSum)` por cliente |
| `Monetary_Log` | Log1p de Monetary (reduce outliers) | `log1p(Monetary)` |
| `Frequency_Log` | Log1p de Frequency | `log1p(Frequency)` |

### Features Avanzadas

| Columna | Descripción |
|---------|-------------|
| `AvgTicket` | Ticket promedio por factura = `mean(TotalSum por Invoice)` |
| `DaysBetweenPurchases` | Promedio de días entre compras consecutivas |
| `MonetaryStdDev` | Desviación estándar del gasto (consistencia del cliente) |
| `UniqueProducts` | Número de StockCodes únicos comprados |
| `PeakHourBuyer` | Proporción de compras realizadas entre 10h-14h |

### Etiquetado (`data/processed/rfm_with_churn.parquet`)

| Columna | Valores | Descripción |
|---------|---------|-------------|
| `CHURN` | `0`, `1` | `1` si Recency > 90 días (inactivo), `0` si activo |

### Segmentación (`data/processed/final_customer_results.parquet`)

| Columna | Valores | Descripción |
|---------|---------|-------------|
| `ChurnProbability` | `[0.0, 1.0]` | Probabilidad de abandono estimada por el modelo |
| `RiskSegment` | `Riesgo Muy Alto`, `Riesgo Medio`, `Estable (Riesgo Bajo)` | Categoría de riesgo basada en ChurnProbability |
| `R_Score` | `1-4` | Score de Recency (4 = más reciente) |
| `F_Score` | `1-4` | Score de Frequency (4 = más frecuente) |
| `M_Score` | `1-4` | Score de Monetary (4 = mayor gasto) |
| `RFM_Group` | Código 3 dígitos | Concatenación de R+F+M scores, ej. `"443"` |
| `RFM_Score` | `3-12` | Suma de R+F+M scores |
| `CustomerLevel` | `VIP / Champion`, `Leales / Prometedores`, `En Riesgo / Perdidos` | Nivel basado en RFM_Score |

---

## Notas de Calidad de Datos

> [!WARNING]
> - **~25% de las transacciones** no tienen `Customer ID` y se eliminan en preprocesamiento.
> - Existen **precios = 0** (posiblemente muestras o errores) — se filtran con `min_price=0.01`.
> - Cantidades muy altas (>10,000 unidades) son típicas de clientes B2B — no son outliers en ese contexto.
> - El dataset incluye clientes de múltiples países, pero el análisis se realiza a nivel global.
