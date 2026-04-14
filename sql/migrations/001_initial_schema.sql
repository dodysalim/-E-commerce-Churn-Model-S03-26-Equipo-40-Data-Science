-- ============================================================
-- Migración 001: Schema Inicial del Proyecto Churn E-Commerce
-- Equipo 40 — No Country
-- ============================================================

-- Tabla principal de resultados por cliente
CREATE TABLE IF NOT EXISTS customer_churn_results (
    id                  BIGSERIAL PRIMARY KEY,
    customer_id         TEXT NOT NULL UNIQUE,
    recency             INTEGER,            -- Días desde última compra
    frequency           INTEGER,            -- Número de facturas únicas
    monetary            NUMERIC(12, 2),     -- Gasto total histórico (£)
    churn               SMALLINT CHECK (churn IN (0, 1)),
    churn_probability   NUMERIC(6, 4),      -- [0.0000, 1.0000]
    risk_segment        TEXT CHECK (risk_segment IN (
                            'Riesgo Muy Alto',
                            'Riesgo Medio',
                            'Estable (Riesgo Bajo)'
                        )),
    customer_level      TEXT CHECK (customer_level IN (
                            'VIP / Champion',
                            'Leales / Prometedores',
                            'En Riesgo / Perdidos'
                        )),
    rfm_score           SMALLINT,           -- Score RFM total (3-12)
    r_score             SMALLINT,           -- Score Recency (1-4)
    f_score             SMALLINT,           -- Score Frequency (1-4)
    m_score             SMALLINT,           -- Score Monetary (1-4)
    avg_ticket          NUMERIC(10, 2),     -- Ticket promedio por factura
    unique_products     INTEGER,            -- Número de productos únicos comprados
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_customer_churn_results
    BEFORE UPDATE ON customer_churn_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comentarios de columnas para documentación en Power BI
COMMENT ON TABLE customer_churn_results IS 
    'Resultados del modelo de predicción de churn. Actualizado por el pipeline de ML.';
COMMENT ON COLUMN customer_churn_results.churn IS 
    '1 = Cliente inactivo >90 días (Churn), 0 = Cliente activo';
COMMENT ON COLUMN customer_churn_results.churn_probability IS 
    'Probabilidad estimada de abandono entre 0 y 1 (priorizar valores altos)';
COMMENT ON COLUMN customer_churn_results.risk_segment IS 
    'Segmento de riesgo basado en churn_probability';
