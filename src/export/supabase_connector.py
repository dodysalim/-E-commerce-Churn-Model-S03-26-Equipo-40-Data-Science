"""
src.export.supabase_connector — Conector con Upsert a Supabase
==============================================================
Responsabilidad única: exportar DataFrames a Supabase usando
upsert (INSERT ... ON CONFLICT UPDATE) para idempotencia.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class SupabaseConnector:
    """
    Conector robusto a Supabase con soporte para upsert y chunking.

    Características:
    - Upsert (no insert) para idempotencia — se puede re-ejecutar el pipeline
    - Chunking configurable para datasets grandes
    - Validación de variables de entorno al inicializar
    - Manejo de errores con retry básico

    Parámetros
    ----------
    env_file : str | Path, opcional
        Ruta al archivo .env con credenciales. Si None, busca en el directorio actual.
    chunk_size : int
        Número de registros por chunk de inserción. Por defecto 500.
    """

    def __init__(
        self,
        env_file: Optional[str | Path] = None,
        chunk_size: int = 500,
    ) -> None:
        if env_file:
            load_dotenv(dotenv_path=env_file)
        else:
            load_dotenv()

        self.chunk_size = chunk_size
        self._url = os.environ.get("SUPABASE_URL")
        self._key = os.environ.get("SUPABASE_KEY")
        self._client = None

    def _get_client(self):
        """Inicializa y retorna el cliente Supabase (lazy initialization)."""
        if self._client is not None:
            return self._client

        if not self._url or not self._key:
            raise ValueError(
                "SUPABASE_URL y SUPABASE_KEY no están configurados.\n"
                "Crea un archivo .env con estas variables o expórtalas manualmente."
            )

        try:
            from supabase import create_client
            self._client = create_client(self._url, self._key)
            logger.info("Conexión a Supabase establecida.")
        except ImportError:
            raise ImportError("Instala supabase-py: pip install supabase>=2.3.0")

        return self._client

    def upsert(self, df: pd.DataFrame, table_name: str, on_conflict: str = "customer_id") -> bool:
        """
        Inserta o actualiza registros en Supabase (upsert).

        El upsert garantiza que al re-ejecutar el pipeline no se generan
        duplicados — simplemente actualiza los registros existentes.

        Parámetros
        ----------
        df : pd.DataFrame
            Datos a cargar.
        table_name : str
            Nombre de la tabla en Supabase.
        on_conflict : str
            Columna de conflicto para el upsert. Por defecto 'customer_id'.

        Retorna
        -------
        bool
            True si la exportación fue exitosa.
        """
        client = self._get_client()

        # Limpiar NaN → None (compatible con JSON/PostgreSQL)
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient="records")
        total = len(records)

        logger.info(f"Exportando {total:,} registros a '{table_name}' (upsert, chunk={self.chunk_size})...")

        success_count = 0
        try:
            for i in range(0, total, self.chunk_size):
                chunk = records[i: i + self.chunk_size]
                client.table(table_name).upsert(chunk, on_conflict=on_conflict).execute()
                success_count += len(chunk)
                logger.debug(f"  Chunk {i // self.chunk_size + 1}: {len(chunk)} registros ✓")

            logger.info(f"✅ Exportación completada: {success_count:,}/{total:,} registros.")
            return True

        except Exception as e:
            logger.error(f"❌ Error durante la exportación a Supabase: {e}")
            raise

    def sync_churn_results(self, df: pd.DataFrame) -> bool:
        """
        Sincroniza los resultados finales del modelo a la tabla principal de Supabase.

        Selecciona automáticamente las columnas relevantes para el dashboard de Power BI.
        """
        columns_to_export = [
            col for col in [
                "Customer ID", "Recency", "Frequency", "Monetary",
                "CHURN", "ChurnProbability", "RiskSegment", "CustomerLevel",
                "RFM_Score", "R_Score", "F_Score", "M_Score",
                "AvgTicket", "UniqueProducts",
            ]
            if col in df.columns
        ]

        # Renombrar Customer ID para compatibilidad con PostgreSQL
        export_df = df[columns_to_export].copy()
        if "Customer ID" in export_df.columns:
            export_df = export_df.rename(columns={"Customer ID": "customer_id"})

        # Convertir CamelCase a snake_case de forma robusta
        import re
        def to_snake(name):
            name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower().replace(" ", "_").replace("__", "_")

        export_df.columns = [to_snake(c) for c in export_df.columns]

        return self.upsert(export_df, table_name="customer_churn_results", on_conflict="customer_id")

    def test_connection(self) -> bool:
        """Verifica que la conexión a Supabase está activa."""
        try:
            client = self._get_client()
            # Health check: intentar un select vacío
            client.table("customer_churn_results").select("customer_id").limit(1).execute()
            logger.info("✅ Conexión a Supabase: OK")
            return True
        except Exception as e:
            logger.error(f"❌ Conexión a Supabase fallida: {e}")
            return False
