from datetime import date

from loguru import logger
from src.ingestion.fideDownloader import FideDownloader
from src.ingestion.dataParser import DataParser
from src.ingestion.parquetLoader import ParquetLoader
from src.models.player import FidePlayer
from src.config.settings import FIDE_DOWNLOAD_URL
from src.utils.snapshot import interim_path

class IngestionController:
    """Controlador principal para el pipeline de ingesta de datos de la FIDE."""

    def __init__(self, snapshot: date):
        self.snapshot = snapshot

    def validate_stream(self, data_stream):
        """Convierte cada diccionario extraído en un modelo Pydantic y retorna un diccionario validado."""
        for record in data_stream:
            player = FidePlayer(**record)
            yield player.model_dump()
            
    def run_pipeline(self, force_download: bool = False):
        logger.info("[Kepler ChessAnalitic - Pipeline de Ingestión]")

        output_path = interim_path(self.snapshot)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        downloader = FideDownloader(url=FIDE_DOWNLOAD_URL, snapshot=self.snapshot)
        ruta_zip = downloader.download_data(force=force_download)

        extractor = DataParser(zip_path=str(ruta_zip), snapshot=self.snapshot)
        flujo_datos = extractor.parse()
        
        logger.info("Validando tipos de datos con Pydantic...")
        flujo_validado = self.validate_stream(flujo_datos)

        # 4. Guardar en Parquet
        cargador = ParquetLoader(output_path=str(output_path))
        cargador.save(flujo_validado)

        logger.info("[Pipeline finalizado con éxito]")
