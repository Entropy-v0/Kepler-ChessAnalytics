from loguru import logger
from ingestion.fideDownloader import FideDownloader
from ingestion.dataParser import DataParser
from ingestion.parquetLoader import ParquetLoader
from models.player import FidePlayer
from config.settings import FIDE_DOWNLOAD_URL, INTERIM_PARQUET_PATH

class IngestionController:
    """Controlador principal para el pipeline de ingesta de datos de la FIDE."""

    def validate_stream(self, data_stream):
        """Convierte cada diccionario extraído en un modelo Pydantic y retorna un diccionario validado."""
        for record in data_stream:
            player = FidePlayer(**record)
            yield player.model_dump()
            
    def run_pipeline(self):
        logger.info("[Kepler ChessAnalitic - Pipeline de Ingestión]")

        INTERIM_PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        downloader = FideDownloader(url=FIDE_DOWNLOAD_URL)
        ruta_zip = downloader.download_data(force=False)

        extractor = DataParser(zip_path=str(ruta_zip))
        flujo_datos = extractor.parse()
        
        logger.info("Validando tipos de datos con Pydantic...")
        flujo_validado = self.validate_stream(flujo_datos)

        # 4. Guardar en Parquet
        cargador = ParquetLoader(output_path=str(INTERIM_PARQUET_PATH))
        cargador.save(flujo_validado)

        logger.info("[Pipeline finalizado con éxito]")
