-- ============================================================
-- Migración 002: Índices de Rendimiento para Power BI
-- ============================================================

-- Índices para columnds de alta frecuencia de filtro en Power BI
CREATE INDEX IF NOT EXISTS idx_churn_results_customer_id 
    ON customer_churn_results(customer_id);

CREATE INDEX IF NOT EXISTS idx_churn_results_risk_segment 
    ON customer_churn_results(risk_segment);

CREATE INDEX IF NOT EXISTS idx_churn_results_customer_level 
    ON customer_churn_results(customer_level);

CREATE INDEX IF NOT EXISTS idx_churn_results_churn 
    ON customer_churn_results(churn);

-- Índice compuesto para consultas VIP en riesgo (vista v_vips_at_risk)
CREATE INDEX IF NOT EXISTS idx_churn_results_vip_risk 
    ON customer_churn_results(customer_level, risk_segment);

-- Índice para ordenación por probabilidad de churn
CREATE INDEX IF NOT EXISTS idx_churn_results_prob 
    ON customer_churn_results(churn_probability DESC);

-- Índice temporal para análisis de tendencias
CREATE INDEX IF NOT EXISTS idx_churn_results_updated_at 
    ON customer_churn_results(updated_at DESC);
