import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from loguru import logger
from typing import Iterator, Dict, Any

class ParquetLoader:
    """
    Clase encargada de consumir el flujo de datos de la FIDE 
    y guardarlo de forma segura (atómica) en formato Parquet,
    utilizando bloques (chunks) para evitar colapsar la memoria RAM.
    """
    def __init__(self, output_path: str, chunk_size: int = 50000):
        self.output_path = output_path
        self.chunk_size = chunk_size

    def save(self, data_iterator: Iterator[Dict[str, Any]]) -> None:
        temp_path = f"{self.output_path}.tmp"
        writer = None
        
        try:
            logger.info(f"Iniciando guardado por bloques de {self.chunk_size} para ahorrar memoria...")
            
            chunk = []
            total_rows = 0

            for record in data_iterator:
                chunk.append(record)
                
                if len(chunk) >= self.chunk_size:
                    df = pd.DataFrame(chunk)
                    table = pa.Table.from_pandas(df)
                    
                    if writer is None:
                        writer = pq.ParquetWriter(temp_path, table.schema)
                    
                    writer.write_table(table)
                    total_rows += len(chunk)
                    chunk = []  
                    
            if chunk:
                df = pd.DataFrame(chunk)
                table = pa.Table.from_pandas(df)
                
                if writer is None:
                    writer = pq.ParquetWriter(temp_path, table.schema)
                
                writer.write_table(table)
                total_rows += len(chunk)

            if writer is not None:
                writer.close()
            
            if total_rows == 0:
                logger.warning("El iterador no devolvió datos. No se guardó ningún archivo.")
                return

            os.replace(temp_path, self.output_path)
            logger.success(f"Archivo Parquet guardado exitosamente (total de registros: {total_rows})")
            
        except Exception as e:
            logger.error(f"Error fatal durante la carga de datos: {e}")
            if writer is not None:
                writer.close()
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(" Archivo temporal eliminado por seguridad.")
            raise e