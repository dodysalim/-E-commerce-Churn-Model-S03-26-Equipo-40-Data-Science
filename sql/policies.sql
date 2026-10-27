-- ============================================================
-- Políticas de Row Level Security (RLS) — Supabase
-- ============================================================

-- 1. Activar RLS en las tablas
ALTER TABLE customer_churn_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_runs ENABLE ROW LEVEL SECURITY;

-- 2. Limpiar políticas anteriores (usaban auth.role(), obsoleto)
DROP POLICY IF EXISTS public_read_churn_results ON customer_churn_results;
DROP POLICY IF EXISTS service_write_churn_results ON customer_churn_results;
DROP POLICY IF EXISTS service_full_access_model_runs ON model_runs;

-- 3. Lectura pública: dashboard y Power BI con la clave pública (anon).
--    Los datos son del dataset público Online Retail II (UCI) con IDs anónimos.
CREATE POLICY public_read_churn_results ON customer_churn_results
    FOR SELECT TO anon, authenticated
    USING (true);

-- 4. Sin políticas de escritura: service_role se salta RLS y el pipeline
--    escribe con esa clave. model_runs queda sin acceso para anon/authenticated.

-- ─── NOTAS ──────────────────────────────────────────────────
-- 1. El dashboard y Power BI usan la ANON KEY (solo lectura).
-- 2. El pipeline usa la SERVICE_ROLE KEY para escritura.
-- 3. Nunca exponer la service_role_key en el frontend.
