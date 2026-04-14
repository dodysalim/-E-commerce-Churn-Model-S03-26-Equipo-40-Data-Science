-- ============================================================
-- Migración 003: Tabla de Registro de Ejecuciones del Modelo
-- ============================================================
-- Permite trazabilidad de cuándo se entrenó cada versión del modelo
-- y qué métricas obtuvo. Útil para auditoría y monitoreo de drift.

CREATE TABLE IF NOT EXISTS model_runs (
    id              BIGSERIAL PRIMARY KEY,
    run_id          TEXT NOT NULL UNIQUE,       -- UUID de la ejecución
    model_name      TEXT NOT NULL,              -- 'XGBoost', 'RandomForest', etc.
    model_version   TEXT NOT NULL,              -- Versión del registry (e.g., 'v20240410')
    recall          NUMERIC(6, 4),
    f1_score        NUMERIC(6, 4),
    roc_auc         NUMERIC(6, 4),
    accuracy        NUMERIC(6, 4),
    n_train_samples INTEGER,
    n_test_samples  INTEGER,
    churn_rate_pct  NUMERIC(5, 2),
    threshold_days  INTEGER,
    features        JSONB,                      -- Lista de features usadas
    hyperparams     JSONB,                      -- Hiperparámetros del modelo
    dataset_hash    TEXT,                       -- SHA256 del dataset para reproducibilidad
    is_champion     BOOLEAN DEFAULT FALSE,      -- True = modelo activo en producción
    run_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Solo puede haber un champion activo a la vez
CREATE UNIQUE INDEX IF NOT EXISTS idx_model_runs_champion 
    ON model_runs(is_champion) WHERE is_champion = TRUE;

-- Índice para consultar el historial de ejecuciones por fecha
CREATE INDEX IF NOT EXISTS idx_model_runs_run_at 
    ON model_runs(run_at DESC);

COMMENT ON TABLE model_runs IS 
    'Registro de cada ejecución del pipeline de entrenamiento. Permite auditoría y detección de drift.';
