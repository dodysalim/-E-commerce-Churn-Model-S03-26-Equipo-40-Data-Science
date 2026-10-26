# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [Versionado Semántico](https://semver.org/lang/es/).

## [1.1.0] - 2026-10-26

### 🔧 Mantenimiento

- **Corregido:** `streamlit` faltaba en `requirements.txt`; el dashboard y sus pruebas no se podían instalar desde cero.
- **Corregido:** conflicto entre `numpy<2` y versiones recientes de `pyarrow` que rompía la página *Plan de Acción*; `pyarrow` queda fijado a `<20`.
- Verificación: 25 pruebas aprobadas y las 6 páginas del dashboard abren sin excepciones en modo demo.
- README con insignias de CI y versión.
