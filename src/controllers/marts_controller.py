"""
src/controllers/marts_controller.py
====================================
Controlador para orquestar la generación de todos los Data Marts analíticos (Capa Oro).
"""

from pathlib import Path
import pandas as pd
from loguru import logger

from src.config.settings import (
    PROCESSED_ALL_PATH,
    PROCESSED_ACTIVE_PATH,
    DATA_MARTS_DIR,
)
from src.marts.global_marts import build_global_marts
from src.marts.elo_marts import build_elo_marts
from src.marts.demographic_marts import build_demographic_marts
from src.marts.youth_marts import build_youth_marts
from src.marts.venezuela_marts import build_venezuela_marts


class MartsController:
    """Orquesta la construcción determinista de los Data Marts para la plataforma de datos."""

    def __init__(
        self,
        all_path: Path = PROCESSED_ALL_PATH,
        active_path: Path = PROCESSED_ACTIVE_PATH,
        output_dir: Path = DATA_MARTS_DIR,
    ):
        self.all_path = Path(all_path)
        self.active_path = Path(active_path)
        self.output_dir = Path(output_dir)

    def run_pipeline(self) -> None:
        """Ejecuta la generación batch de todos los Data Marts."""
        logger.info("[Kepler ChessAnalitic - Pipeline de Data Marts (Capa Oro)]")

        if not self.all_path.exists() or not self.active_path.exists():
            raise FileNotFoundError(
                f"Archivos procesados no encontrados en {self.all_path} o {self.active_path}. "
                "Ejecute primero la fase de procesamiento."
            )

        logger.info(f"Cargando dataset maestro general desde {self.all_path}...")
        df_all = pd.read_parquet(self.all_path)

        logger.info(f"Cargando dataset maestro activo desde {self.active_path}...")
        df_active = pd.read_parquet(self.active_path)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generar cada Data Mart
        build_global_marts(df_all, df_active, self.output_dir)
        build_elo_marts(df_all, self.output_dir)
        build_demographic_marts(df_active, self.output_dir)
        build_youth_marts(df_active, self.output_dir)
        build_venezuela_marts(df_active, self.output_dir)

        # Balance de archivos generados
        logger.info("=== Balance de Data Marts Generados ===")
        total_size = 0
        for mart_file in sorted(self.output_dir.glob("*.parquet")):
            size = mart_file.stat().st_size
            total_size += size
            logger.info(f" -> {mart_file.name:<35} | {size:>10,} bytes ({size / 1024:.2f} KB)")

        logger.success(
            f"[Pipeline de Data Marts finalizado con éxito | Total almacenamiento: {total_size / (1024*1024):.2f} MB]"
        )
