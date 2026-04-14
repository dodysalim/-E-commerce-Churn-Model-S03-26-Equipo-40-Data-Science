-- Esquema para resultados de Churn E-commerce (Versión Enterprise Resiliente)

DROP TABLE IF EXISTS customer_churn_results;

CREATE TABLE customer_churn_results (
    id SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    recency FLOAT,
    frequency FLOAT,
    monetary FLOAT,
    rfm_score FLOAT,
    r_score FLOAT,
    f_score FLOAT,
    m_score FLOAT,
    avg_ticket FLOAT,
    unique_products FLOAT,
    churn INT,
    churn_probability FLOAT,
    risk_segment TEXT,
    customer_level TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar el rendimiento en Power BI
CREATE INDEX IF NOT EXISTS idx_customer_id ON customer_churn_results(customer_id);
CREATE INDEX IF NOT EXISTS idx_risk_segment ON customer_churn_results(risk_segment);
CREATE INDEX IF NOT EXISTS idx_customer_level ON customer_churn_results(customer_level);
CREATE INDEX IF NOT EXISTS idx_churn_prob ON customer_churn_results(churn_probability);

-- Tabla para el historial de ejecuciones (MLOps básico)
CREATE TABLE IF NOT EXISTS model_runs (
    id SERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    run_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    recall FLOAT,
    accuracy FLOAT,
    f1_score FLOAT,
    roc_auc FLOAT,
    status TEXT DEFAULT 'success'
);