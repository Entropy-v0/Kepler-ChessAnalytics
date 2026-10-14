"""
src/controllers/processing_controller.py
=========================================
Controlador encargado de la fase de procesamiento (Interim -> Processed).
"""

from datetime import date
from pathlib import Path
from typing import Optional
import pandas as pd
from loguru import logger

from src.config.settings import PROCESSED_ALL_FILENAME, PROCESSED_ACTIVE_FILENAME
from src.processing.cleaner import DataCleaner
from src.processing.feature_builder import FeatureBuilder
from src.utils.snapshot import interim_path, processed_dir


class ProcessingController:
    """Orquesta la limpieza y enriquecimiento de los datos desde Interim hasta Processed."""

    def __init__(self, snapshot: date, input_path: Optional[Path] = None, all_output_path: Optional[Path] = None, active_output_path: Optional[Path] = None ):
        
        self.snapshot = snapshot
        out_dir = processed_dir(snapshot)
        self.input_path = Path(input_path) if input_path else interim_path(snapshot)
        self.all_output_path = Path(all_output_path) if all_output_path else out_dir / PROCESSED_ALL_FILENAME
        self.active_output_path = (
            Path(active_output_path) if active_output_path else out_dir / PROCESSED_ACTIVE_FILENAME
        )
        self.cleaner = DataCleaner()
        self.feature_builder = FeatureBuilder(reference_year=snapshot.year)

    def run_pipeline(self) -> None:
        """Ejecuta el pipeline completo de procesamiento."""
        logger.info("[Kepler ChessAnalitic - Pipeline de Procesamiento]")

        if not self.input_path.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo de entrada: {self.input_path}. "
                "Ejecute primero la fase de ingestión."
            )

        logger.info(f"Cargando dataset bruto desde {self.input_path}...")
        df_raw = pd.read_parquet(self.input_path)

        # 1. Limpieza
        df_clean = self.cleaner.clean(df_raw)

        # 2. Ingeniería de características
        df_enriched = self.feature_builder.build_features(df_clean)

        # 3. Segmentación
        df_all, df_active = self.feature_builder.split_datasets(df_enriched)

        # 4. Guardado en Parquet
        self.all_output_path.parent.mkdir(parents=True, exist_ok=True)
        self.active_output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Guardando padrón general en {self.all_output_path}...")
        df_all.to_parquet(self.all_output_path, index=False)

        logger.info(f"Guardando padrón activo en {self.active_output_path}...")
        df_active.to_parquet(self.active_output_path, index=False)

        logger.success("[Pipeline de procesamiento finalizado con éxito]")
