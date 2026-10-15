"""
src/processing/cleaner.py
==========================
Módulo de limpieza y depuración de datos brutos del padrón FIDE.
Aplica reglas deterministas de calidad de datos.
"""

from typing import List
import numpy as np
import pandas as pd
from loguru import logger
from src.config.constants import TITLES_COLUMNS, MIN_BIRTH_YEAR


class DataCleaner:
    """Clase encargada de sanear y filtrar los datos brutos del archivo fide_players_bruto."""

    TITLES_COLUMNS: List[str] = TITLES_COLUMNS
    MIN_BIRTH_YEAR: int = MIN_BIRTH_YEAR

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta el pipeline de limpieza sobre el DataFrame bruto.
        
        Reglas aplicadas:
        1. Filtra jugadores que tengan al menos un rating (clásico, rápido o blitz) mayor a 0.
        2. Reemplaza ratings iguales a 0 por NaN.
        3. Descarta registros sin año de nacimiento (birthday nulo).
        4. Descarta registros con año de nacimiento anómalo (< 1920).
        5. Imputa títulos faltantes con 'nt' (No Title).
        6. Elimina duplicados por fideid manteniendo el primer registro.
        """
        initial_len = len(df)
        logger.info(f"Iniciando limpieza de datos. Registros iniciales: {initial_len:,}")

        # 1. Al menos un rating > 0
        has_rating = (
            (df["rating"].fillna(0) > 0)
            | (df["rapid_rating"].fillna(0) > 0)
            | (df["blitz_rating"].fillna(0) > 0)
        )
        df_clean = df[has_rating].copy()
        logger.info(f"Filtrados jugadores con al menos un rating activo: {len(df_clean):,}")

        for col in ["rating", "rapid_rating", "blitz_rating"]:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].replace(0, np.nan)

        df_clean = df_clean.dropna(subset=["birthday"]).copy()

        df_clean["birthday"] = df_clean["birthday"].astype(int)

        df_clean = df_clean[df_clean["birthday"] >= MIN_BIRTH_YEAR].copy()

        for col in TITLES_COLUMNS:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna("nt").replace("", "nt")
            else:
                df_clean[col] = "nt"


        dups = df_clean.duplicated(subset=["fideid"]).sum()
        if dups > 0:
            logger.warning(f"Se encontraron {dups} registros duplicados por fideid. Eliminando...")
            df_clean = df_clean.drop_duplicates(subset=["fideid"], keep="first")

        logger.success(f"Limpieza completada exitosamente. Registros finales limpios: {len(df_clean):,}")
        return df_clean
