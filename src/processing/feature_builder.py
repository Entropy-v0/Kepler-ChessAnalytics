"""
src/processing/feature_builder.py
==================================
Módulo de ingeniería de características para el padrón FIDE.
Calcula edad federativa, banderas de actividad y categorías formativas.
"""

from datetime import datetime
from typing import List, Tuple
import numpy as np
import pandas as pd
from loguru import logger


class FeatureBuilder:
    """Clase encargada de enriquecer el padrón FIDE con variables derivadas y segmentación."""

    ORDERED_CATEGORIES: List[str] = [
        "Sub 8", "Sub 10", "Sub 12", "Sub 14",
        "Sub 16", "Sub 18", "Sub 20", "Absoluta"
    ]

    def __init__(self, reference_year: int = None):
        self.reference_year = reference_year or datetime.now().year

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula edad, actividad y categorías oficiales FIDE."""
        df_feat = df.copy()
        logger.info(f"Generando features con año de referencia {self.reference_year}...")

        df_feat["flag"] = df_feat["flag"].fillna("").astype(str)
        df_feat["es_activo"] = ~df_feat["flag"].isin(["i", "wi"])

        df_feat["edad"] = self.reference_year - df_feat["birthday"].astype(int)

        condiciones = [
            (df_feat["edad"] > 0) & (df_feat["edad"] < 8),
            (df_feat["edad"] >= 8) & (df_feat["edad"] < 10),
            (df_feat["edad"] >= 10) & (df_feat["edad"] < 12),
            (df_feat["edad"] >= 12) & (df_feat["edad"] < 14),
            (df_feat["edad"] >= 14) & (df_feat["edad"] < 16),
            (df_feat["edad"] >= 16) & (df_feat["edad"] < 18),
            (df_feat["edad"] >= 18) & (df_feat["edad"] < 20),
            (df_feat["edad"] >= 20),
        ]

        df_feat["categoria"] = np.select(
            condiciones,
            self.ORDERED_CATEGORIES,
            default="Sin Categoría"
        )

        df_feat["categoria"] = pd.Categorical(
            df_feat["categoria"],
            categories=self.ORDERED_CATEGORIES,
            ordered=True
        )

        logger.success(f"Features construidas exitosamente ({len(df_feat):,} registros).")
        return df_feat

    def split_datasets(self, df_enriched: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Segmenta en:
        1. df_all: Padrón total limpio.
        2. df_active: Padrón de activos (flag != 'i'/'wi') con edad <= 95 años.
        """
        df_all = df_enriched.copy()

        df_active = df_enriched[
            df_enriched["es_activo"] & (df_enriched["edad"] <= 95)
        ].copy()

        logger.info(f"Padrón general: {len(df_all):,} registros | Padrón activo: {len(df_active):,} registros.")
        return df_all, df_active
