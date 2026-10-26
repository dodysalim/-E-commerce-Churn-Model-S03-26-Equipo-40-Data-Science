"""
src.export.schema_deployer — Despliegue de Schema en Supabase
=============================================================
Responsabilidad única: ejecutar los archivos SQL de schema y
views en Supabase vía conexión directa a PostgreSQL.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class SchemaDeployer:
    """
    Despliega el schema SQL en Supabase usando SQLAlchemy + psycopg2.

    Requiere la variable de entorno SUPABASE_DB_URL (connection string
    de PostgreSQL directo, no la URL de la API).

    Formato esperado:
    postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

    Parámetros
    ----------
    sql_dir : str | Path
        Directorio con los archivos SQL. Por defecto 'sql'.
    """

    def __init__(self, sql_dir: str | Path = "sql") -> None:
        load_dotenv()
        self.sql_dir = Path(sql_dir)
        self._db_url = os.environ.get("SUPABASE_DB_URL")

    def _get_engine(self):
        """Crea el engine SQLAlchemy."""
        if not self._db_url:
            raise ValueError(
                "SUPABASE_DB_URL no está configurado en el .env.\n"
                "Formato: postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres"
            )
        try:
            from sqlalchemy import create_engine
            return create_engine(self._db_url)
        except ImportError:
            raise ImportError("Instala sqlalchemy y psycopg2-binary.")

    def deploy_schema(self) -> bool:
        """
        Ejecuta el archivo de schema principal (sql/migrations/).

        Retorna
        -------
        bool
            True si el despliegue fue exitoso.
        """
        migrations_dir = self.sql_dir / "migrations"
        if not migrations_dir.exists():
            logger.warning(f"No se encontró el directorio de migraciones: {migrations_dir}")
            return False

        engine = self._get_engine()
        migration_files = sorted(migrations_dir.glob("*.sql"))

        if not migration_files:
            logger.warning("No hay archivos de migración en sql/migrations/")
            return False

        logger.info(f"Desplegando {len(migration_files)} migraciones...")
        with engine.connect() as conn:
            for sql_file in migration_files:
                sql_content = sql_file.read_text(encoding="utf-8")
                logger.info(f"  Ejecutando: {sql_file.name}")
                conn.execute(sql_content)  # type: ignore
            conn.commit()

        logger.info("✅ Schema desplegado exitosamente en Supabase.")
        return True

    def deploy_views(self) -> bool:
        """Ejecuta el archivo views.sql para crear/actualizar las vistas de Power BI."""
        views_file = self.sql_dir / "views.sql"
        if not views_file.exists():
            logger.error(f"No se encontró: {views_file}")
            return False

        engine = self._get_engine()
        with engine.connect() as conn:
            conn.execute(views_file.read_text(encoding="utf-8"))  # type: ignore
            conn.commit()

        logger.info("✅ Vistas Power BI desplegadas exitosamente.")
        return True
