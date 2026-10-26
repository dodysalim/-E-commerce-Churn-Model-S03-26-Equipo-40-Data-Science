-- ============================================================
-- Políticas de Row Level Security (RLS) — Supabase
-- ============================================================

-- 1. Activar RLS en las tablas
ALTER TABLE customer_churn_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_runs ENABLE ROW LEVEL SECURITY;

-- 2. Crear Políticas de forma segura (Idempotentes)
DO $$ 
BEGIN
    -- Política para lectura pública (Power BI)
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'public_read_churn_results') THEN
        CREATE POLICY "public_read_churn_results" ON customer_churn_results 
        FOR SELECT USING (true);
    END IF;

    -- Política para escritura del Pipeline (Service Role)
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'service_write_churn_results') THEN
        CREATE POLICY "service_write_churn_results" ON customer_churn_results 
        FOR ALL USING (auth.role() = 'service_role');
    END IF;

    -- Política para historial de modelos (Solo Service Role)
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'service_full_access_model_runs') THEN
        CREATE POLICY "service_full_access_model_runs" ON model_runs 
        FOR ALL USING (auth.role() = 'service_role');
    END IF;
END $$;

-- ─── NOTAS ──────────────────────────────────────────────────
-- 1. Power BI debe conectarse con la ANON KEY para lectura.
-- 2. El pipeline usa la SERVICE_ROLE KEY para escritura.
-- 3. Nunca exponer la service_role_key en el frontend.