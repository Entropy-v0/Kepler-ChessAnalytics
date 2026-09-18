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
DATA_MARTS_DIR = ROOT_DIR / "data" / "marts"

INTERIM_PARQUET_PATH = DATA_INTERIM_DIR / "fide_players_bruto.parquet"
PROCESSED_ALL_PATH = DATA_PROCESSED_DIR / "fide_players_all.parquet"
PROCESSED_ACTIVE_PATH = DATA_PROCESSED_DIR / "fide_players_active.parquet"

# Rutas de Data Marts (Capa Oro)
MART_GLOBAL_PATH = DATA_MARTS_DIR / "mart_panorama_global.parquet"
MART_ELO_PATH = DATA_MARTS_DIR / "mart_distribucion_elo.parquet"
MART_TITULOS_PATH = DATA_MARTS_DIR / "mart_titulos_federacion.parquet"
MART_DEMOGRAFIA_PATH = DATA_MARTS_DIR / "mart_demografia_genero.parquet"
MART_YOUTH_PATH = DATA_MARTS_DIR / "mart_cohortes_juveniles.parquet"
MART_VENEZUELA_PATH = DATA_MARTS_DIR / "mart_venezuela.parquet"

FIDE_DOWNLOAD_URL: str = os.getenv("URL_DESCARGA", "")

if not FIDE_DOWNLOAD_URL:
    logger.warning("La variable URL_DESCARGA no está definida en el archivo .env")

