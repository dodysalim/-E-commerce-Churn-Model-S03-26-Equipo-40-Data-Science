# Churn Intelligence — Power BI

DEMOSTRACIÓN SINTÉTICA del Streamlit original · 800 clientes · no son predicciones de producción

## Abrir

1. Descarga el repositorio completo.
2. Ejecuta `python powerbi/configure_data.py`. Alternativamente, en Transformar datos → Administrar parámetros cambia `DataFolder` a la carpeta `powerbi/data/` con separador final.
3. Abre `powerbi/Analytics.pbip` en Power BI Desktop y pulsa Actualizar.

## Estructura y correspondencia

Cinco páginas equivalentes a las cinco secciones de Streamlit. Los CSV proceden exclusivamente de `_generate_demo_data()` del proyecto, semilla 42. La tasa global y los agregados se calculan de la misma tabla de 800 clientes; se omiten los KPIs globales estáticos del demo que no coinciden con sus filas. Supabase no está conectado. Para producción exporta las vistas sin renormalizar importes ni generar valores ficticios.

Las páginas conservan el análisis del proyecto original. Los controles de entrenamiento, conexión, escritura SQL e inferencia en vivo siguen en Python/Streamlit. El informe consume resultados exportados; no reemplaza esos servicios. Los CSV conservan su grano, y las medidas evitan sumar porcentajes o promedios.

## Verificación de esta entrega

El serializador TMDL nativo instalado con Power BI Desktop aceptó el modelo. Se comprobaron las referencias de los campos y los límites de cada visual. Esto valida la estructura; la apertura, actualización y representación de los gráficos se comprueban por separado. Los proyectos sin datos siguen pendientes.

Para regenerar los CSV y el informe desde las fuentes del repositorio: `python powerbi/rebuild_report.py`, seguido de `python powerbi/configure_data.py`. Requiere pandas, numpy y scikit-learn; M5 y atención al cliente también scipy; M5 openpyxl. Los datos externos deben descargarse antes.

## Presentación y selección

Lienzo ampliado a 1280×1040, tarjetas sin abreviación automática, filtros con su propio encabezado y tablas con más espacio. El ciclo muestra «Selecciona escenario» hasta elegir un único gas, temperatura de evaporación y condensación. Los proyectos sin datos muestran «Datos pendientes»; no se sustituyen datos desconocidos por ceros.

Después de regenerar el informe, ejecuta `python powerbi/polish_report.py` para aplicar los ajustes de presentación.

Para abrir en Windows sin rutas fijas ni Python: cierra el informe y haz doble clic en `powerbi/Abrir-PowerBI.bat`. Configura DataFolder con la carpeta extraída; después pulsa Actualizar en Power BI.

## A4 y versión móvil

PC: hoja A4 horizontal (297×210 mm, lienzo 1123×794 a 96 ppp), vista Tamaño real / 100%. Si la ventana es menor que la hoja, amplíala o desplázate por el lienzo.

Móvil: diseño nativo de Power BI de 323 puntos de ancho, con tarjetas, filtros y gráficos apilados, tablas amplias y desplazamiento vertical. Se adapta al teléfono; el tamaño físico de una hoja A4 y el zoom 100% no equivalen en pantallas de distintos tamaños. Consulta Vista > Diseño móvil en Desktop y usa la aplicación Power BI para verlo en el teléfono tras publicar.

Tras reconstruir el informe, ejecuta `python polish_report.py` para recuperar ambas presentaciones. El ajuste es idempotente y conserva medidas, consultas y datos.
