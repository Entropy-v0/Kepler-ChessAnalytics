import requests
from pathlib import Path
from loguru import logger
from tqdm import tqdm

from config.settings import FIDE_DOWNLOAD_URL, DATA_RAW_DIR


class FideDownloader:
    """
    Clase encargada de la extracción (descarga) de los datos crudos de la FIDE.

    Recibe la URL como parámetro explícito (en vez de leerla internamente)
    para facilitar las pruebas y desacoplarla del sistema de configuración.
    """

    DEFAULT_TIMEOUT = 30  # segundos

    def __init__(self, url: str = FIDE_DOWNLOAD_URL, output_dir: Path = DATA_RAW_DIR):
        if not url:
            logger.error("Se requiere una URL de descarga válida.")
            raise ValueError("URL de descarga no puede estar vacía.")

        self.url = url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.filename = self.url.split("/")[-1]
        self.output_path = self.output_dir / self.filename

    def download_data(self, force: bool = False) -> Path:
        """
        Descarga el archivo desde la URL especificada mostrando una barra de progreso.

        Args:
            force: Si es True, descarga aunque el archivo ya exista localmente.

        Returns:
            La ruta local (Path) donde se guardó el archivo crudo.
        """
        if self.output_path.exists() and not force:
            logger.warning(
                f"El archivo ya existe."
            )
            return self.output_path

        logger.info(f"Iniciando descarga desde: {self.url}")

        try:
            response = requests.get(self.url, stream=True, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with open(self.output_path, "wb") as file, tqdm(
                desc=self.filename,
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        size = file.write(chunk)
                        bar.update(size)

            logger.success(f"El archivo se descargó exitosamente en: {self.output_path}")
            return self.output_path

        except requests.exceptions.Timeout:
            logger.error(f"Tiempo de espera agotado ({self.DEFAULT_TIMEOUT}s) al conectar con: {self.url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al intentar descargar el archivo: {e}")
            raise
