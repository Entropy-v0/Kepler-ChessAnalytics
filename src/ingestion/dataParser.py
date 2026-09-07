import zipfile
import xml.etree.ElementTree as ET
from typing import Iterator, Dict, Any
from loguru import logger
from tqdm import tqdm

class DataParser:
    """
    Clase encargada de la extracción (parsing) de los datos crudos de la FIDE en formato XML,
    manteniendo un bajo consumo de memoria mediante streaming.
    """
    def __init__(self, zip_path: str):
        self.zip_path = zip_path

    def parse(self) -> Iterator[Dict[str, Any]]:
        logger.info(f"Abriendo archivo ZIP para extracción: {self.zip_path}")
        
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                xml_filename = z.namelist()[0]
                logger.info(f"Iniciando lectura del flujo XML interno: {xml_filename}")
                
                with z.open(xml_filename) as xml_file:
                    context = ET.iterparse(xml_file, events=('end',))
                    
                    with tqdm(desc="Procesando jugadores", unit=" jug") as pbar:
                        for event, elem in context:
                            if elem.tag == 'player': 
                                
                                player_data = {
                                    "fideid": elem.findtext('fideid'),
                                    "name": elem.findtext('name'),
                                    "country": elem.findtext('country'),
                                    "sex": elem.findtext('sex'),
                                    "title": elem.findtext('title'),
                                    "w_title": elem.findtext('w_title'),
                                    "o_title": elem.findtext('o_title'),
                                    "rating": elem.findtext('rating'),
                                    "rapid_rating": elem.findtext('rapid_rating'),
                                    "blitz_rating": elem.findtext('blitz_rating'),
                                    "birthday": elem.findtext('birthday'),
                                    "flag": elem.findtext('flag')
                                }
                                
                                yield player_data
                                
                                elem.clear()
                                
                                pbar.update(1)
                                
                    logger.success("Lectura en streaming del archivo XML finalizada con éxito.")
                    
        except Exception as e:
            logger.error(f"Error al leer el archivo ZIP o procesar el XML: {e}")
            raise e