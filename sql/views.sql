-- ============================================================
-- Vistas Optimizadas para Power BI — Churn Prediction
-- Equipo 40 — No Country
-- ============================================================

-- ─── 1. Resumen Ejecutivo por Segmento de Riesgo ────────────
CREATE OR REPLACE VIEW v_executive_churn_summary AS
SELECT
    risk_segment,
    COUNT(*)                                          AS total_customers,
    ROUND((AVG(churn_probability) * 100)::numeric, 2) AS avg_churn_risk_pct,
    ROUND(SUM(monetary)::numeric, 2)                  AS total_monetary_exposure,
    ROUND(AVG(monetary)::numeric, 2)                  AS avg_monetary_per_customer,
    ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ())::numeric, 2) AS pct_of_total_customers
FROM customer_churn_results
GROUP BY risk_segment
ORDER BY avg_churn_risk_pct DESC;

-- ─── 2. Matriz Valor vs Riesgo (Scatter Chart en Power BI) ──
CREATE OR REPLACE VIEW v_value_risk_matrix AS
SELECT
    customer_id,
    customer_level,
    risk_segment,
    ROUND(monetary::numeric, 2)          AS monetary,
    ROUND(churn_probability::numeric, 4) AS churn_probability,
    recency,
    frequency,
    rfm_score
FROM customer_churn_results;

-- ─── 3. Clientes VIP en Zona de Riesgo ──────────────────────
CREATE OR REPLACE VIEW v_vips_at_risk AS
SELECT
    customer_id,
    risk_segment,
    ROUND((churn_probability * 100)::numeric, 1)  AS churn_risk_pct,
    ROUND(monetary::numeric, 2)                    AS lifetime_value,
    recency                                        AS days_inactive,
    frequency                                      AS total_purchases,
    rfm_score
FROM customer_churn_results
WHERE customer_level = 'VIP / Champion'
  AND risk_segment IN ('Riesgo Muy Alto', 'Riesgo Medio')
ORDER BY churn_probability DESC, monetary DESC;

-- ─── 4. Top 50 Clientes Prioritarios para Retención ─────────
CREATE OR REPLACE VIEW v_top_priority_customers AS
SELECT
    customer_id,
    customer_level,
    risk_segment,
    ROUND((churn_probability * 100)::numeric, 1)       AS churn_risk_pct,
    ROUND(monetary::numeric, 2)                        AS lifetime_value,
    ROUND((monetary * churn_probability)::numeric, 2)  AS expected_loss,
    recency                                            AS days_inactive,
    rfm_score
FROM customer_churn_results
WHERE risk_segment IN ('Riesgo Muy Alto', 'Riesgo Medio')
ORDER BY expected_loss DESC
LIMIT 50;

-- ─── 5. Distribución de Clientes por Nivel y Segmento ───────
CREATE OR REPLACE VIEW v_customer_distribution AS
SELECT
    customer_level,
    risk_segment,
    COUNT(*)                                           AS customer_count,
    ROUND(AVG(monetary)::numeric, 2)                   AS avg_monetary,
    ROUND((AVG(churn_probability) * 100)::numeric, 2)  AS avg_churn_risk_pct,
    ROUND(AVG(recency)::numeric, 0)                    AS avg_recency_days
FROM customer_churn_results
GROUP BY customer_level, risk_segment
ORDER BY customer_level, risk_segment;

-- ─── 6. Métricas Globales del Modelo (para KPI Banner) ───────
CREATE OR REPLACE VIEW v_global_metrics AS
SELECT
    COUNT(*)                                            AS total_customers_analyzed,
    SUM(churn)                                          AS total_churned,
    ROUND((AVG(churn) * 100)::numeric, 2)               AS overall_churn_rate_pct,
    ROUND(SUM(CASE WHEN risk_segment = 'Riesgo Muy Alto' THEN monetary ELSE 0 END)::numeric, 2)
                                                        AS high_risk_monetary_exposure,
    COUNT(CASE WHEN customer_level = 'VIP / Champion' AND risk_segment != 'Estable (Riesgo Bajo)' THEN 1 END)
                                                        AS vips_at_risk_count,
    MAX(created_at)                                     AS last_model_run
FROM customer_churn_results;