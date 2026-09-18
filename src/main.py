"""
src/main.py
===========
Punto de entrada unificado por CLI para el pipeline ETL de Kepler-ChessAnalitic.
Permite ejecutar el pipeline completo o por fases modulares.
"""

import argparse
import sys
from loguru import logger

from src.config.settings import setup_environment
from src.controllers.ingestion_controller import IngestionController
from src.controllers.processing_controller import ProcessingController
from src.controllers.marts_controller import MartsController


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
        "--force-download",
        action="store_true",
        help="Fuerza la descarga del archivo ZIP aunque ya exista en disco",
    )
    return parser.parse_args()


def run_pipeline(stage: str = "all", force_download: bool = False):
    setup_environment()
    logger.info(f"Iniciando ejecución del pipeline Kepler-ChessAnalitic [Fase: {stage.upper()}]")

    # 1. Ingesta (Raw -> Interim)
    if stage in ["all", "ingest"]:
        logger.info("=== FASE 1: INGESTIÓN (Streaming XML -> Parquet Bruto) ===")
        ingestion = IngestionController()
        # Si se especificó force_download, podemos parametrizarlo si es necesario
        ingestion.run_pipeline()

    # 2. Procesamiento (Interim -> Processed)
    if stage in ["all", "process"]:
        logger.info("=== FASE 2: PROCESAMIENTO (Limpieza y Enriquecimiento) ===")
        processing = ProcessingController()
        processing.run_pipeline()

    # 3. Data Marts (Processed -> Marts)
    if stage in ["all", "marts"]:
        logger.info("=== FASE 3: DATA MARTS (Capa Oro para Streamlit) ===")
        marts = MartsController()
        marts.run_pipeline()

    logger.success(f"Pipeline completado exitosamente para la fase: {stage.upper()}")


def main():
    args = parse_args()
    try:
        run_pipeline(stage=args.stage, force_download=args.force_download)
    except Exception as e:
        logger.error(f"Fallo durante la ejecución del pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()