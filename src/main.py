"""
src/main.py
===========
Punto de entrada unificado por CLI para el pipeline ETL de Kepler-ChessAnalitic.
Permite ejecutar el pipeline completo o por fases modulares.
"""

import argparse
import sys
from datetime import date
from typing import Optional

from loguru import logger

from src.config.settings import (
    setup_environment,
    DATA_INTERIM_DIR,
    DATA_PROCESSED_DIR,
)
from src.controllers.ingestion_controller import IngestionController
from src.controllers.processing_controller import ProcessingController
from src.controllers.marts_controller import MartsController
from src.utils.snapshot import resolve_snapshot, latest_snapshot, snapshot_label


def parse_args():
    parser = argparse.ArgumentParser(
        description="Kepler-ChessAnalitic: Motor ETL y Plataforma de Datos FIDE"
    )
    parser.add_argument(
        "--stage",
        choices=["all", "ingest", "process", "marts"],
        default="all",
        help="Fase del pipeline a ejecutar (default: all)",
    )
    parser.add_argument(
        "--snapshot",
        default=None,
        help="Período a procesar en formato YYYY-MM (default: según la fase)",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Fuerza la descarga del archivo ZIP aunque ya exista en disco",
    )
    return parser.parse_args()


def pick_snapshot(stage: str, value: Optional[str]) -> date:
    """Decide qué snapshot usa la corrida según la fase y el argumento CLI."""
    if value:
        return resolve_snapshot(value)
    if stage in ("all", "ingest"):
        return resolve_snapshot()
    base = DATA_INTERIM_DIR if stage == "process" else DATA_PROCESSED_DIR
    return latest_snapshot(base)


def run_pipeline(stage: str = "all", snapshot_value: Optional[str] = None, force_download: bool = False):
    setup_environment()
    snapshot = pick_snapshot(stage, snapshot_value)
    logger.info(
        f"Iniciando pipeline Kepler-ChessAnalitic [Fase: {stage.upper()} | Snapshot: {snapshot_label(snapshot)}]"
    )

    # 1. Ingesta (Raw -> Interim)
    if stage in ["all", "ingest"]:
        logger.info("=== FASE 1: INGESTIÓN (Streaming XML -> Parquet Bruto) ===")
        IngestionController(snapshot).run_pipeline(force_download=force_download)

    # 2. Procesamiento (Interim -> Processed)
    if stage in ["all", "process"]:
        logger.info("=== FASE 2: PROCESAMIENTO (Limpieza y Enriquecimiento) ===")
        ProcessingController(snapshot).run_pipeline()

    # 3. Data Marts (Processed -> Marts)
    if stage in ["all", "marts"]:
        logger.info("=== FASE 3: DATA MARTS (Capa Oro para Streamlit) ===")
        MartsController(snapshot).run_pipeline()

    logger.success(f"Pipeline completado para la fase {stage.upper()} (snapshot {snapshot_label(snapshot)})")


def main():
    args = parse_args()
    try:
        run_pipeline(
            stage=args.stage,
            snapshot_value=args.snapshot,
            force_download=args.force_download,
        )
    except Exception as e:
        logger.error(f"Fallo durante la ejecución del pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()