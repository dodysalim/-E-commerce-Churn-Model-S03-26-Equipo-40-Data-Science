# Verificación · Churn Intelligence

Fecha: 7 de octubre de 2026 (Ecuador). Entorno local Python 3.12.14. Las dependencias de QA se registran aparte; esta comprobación no certifica todas las combinaciones de versiones del proyecto.

## Ejecutado

25 pruebas aprobadas, incluidas cinco regresiones de datos del dashboard. Inicio y cinco páginas probados en modo demo sin excepciones.

## Dependencias externas y límites

La demostración funciona sin Supabase con 800 clientes sintéticos. Para usar las vistas reales, configura SUPABASE_URL y SUPABASE_KEY (clave de lectura con RLS). Los importes conservan las unidades de origen.

Los datos demo, tendencias ilustrativas y ROI de escenarios no son resultados observados. No se repitió el entrenamiento sobre Online Retail II ni se comprobó Supabase en vivo.

## Presentación Power BI

Las definiciones se revisaron para límites y superposiciones, y el diseño móvil sigue el esquema oficial PBIR. La prueba nativa completa en teléfono permanece pendiente. Las fuentes externas deben exportarse antes de actualizar las páginas sin datos.
