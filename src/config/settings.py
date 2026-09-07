import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def setup_environment():
    """Configura los parámetros globales como el formato de loguru."""
    logger.remove()
    logger.add(
        sys.stderr, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

ROOT_DIR = Path(__file__).parent.parent.parent

DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_INTERIM_DIR = ROOT_DIR / "data" / "interim"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"

INTERIM_PARQUET_PATH = DATA_INTERIM_DIR / "fide_players_bruto.parquet"

FIDE_DOWNLOAD_URL: str = os.getenv("URL_DESCARGA", "")

if not FIDE_DOWNLOAD_URL:
    logger.warning("La variable URL_DESCARGA no está definida en el archivo .env")
