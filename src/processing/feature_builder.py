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

from src.config.constants import (
    AGE_CATEGORY_RULES,
    CAT_ORDER,
    PLAYER_PROFILE_RULES,
    PRO_ORDER,
)


class FeatureBuilder:
    """Clase encargada de enriquecer el padrón FIDE con variables derivadas y segmentación."""

    ORDERED_CATEGORIES: List[str] = CAT_ORDER
    ORDERED_PROFILE: List[str] = PRO_ORDER

    def __init__(self, reference_year: int = None):
        self.reference_year = reference_year or datetime.now().year

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula edad, actividad y categorías oficiales FIDE."""
        df_feat = df.copy()
        logger.info(f"Generando features con año de referencia {self.reference_year}...")

        # 1. Bandera de actividad y limpieza
        if "flag" in df_feat.columns:
            flag_str = df_feat["flag"].fillna("").astype(str).str.strip()
            df_feat["es_activo"] = ~flag_str.isin(["i", "wi"])
            df_feat = df_feat.drop(columns=["flag"])
        else:
            df_feat["es_activo"] = True

        # 2. Edad federativa y Categorías por edad
        df_feat["edad"] = self.reference_year - df_feat["birthday"].astype(int)
        edad = df_feat["edad"]

        condiciones_edad = [
            (edad > min_age) if max_age is None else (edad > min_age) & (edad <= max_age)
            for min_age, max_age in AGE_CATEGORY_RULES.keys()
        ]
        
        df_feat["categoria"] = pd.Categorical(
            np.select(condiciones_edad, self.ORDERED_CATEGORIES, default="sin_categoría"),
            categories=self.ORDERED_CATEGORIES,
            ordered=True,
        )

        # 3. Perfil de ritmo de juego (completo, especialista, mixto)
        has_classic = df_feat["rating"].notna() if "rating" in df_feat.columns else pd.Series(False, index=df_feat.index)
        has_rapid = df_feat["rapid_rating"].notna() if "rapid_rating" in df_feat.columns else pd.Series(False, index=df_feat.index)
        has_blitz = df_feat["blitz_rating"].notna() if "blitz_rating" in df_feat.columns else pd.Series(False, index=df_feat.index)

        condiciones_perfil = [
            (has_classic if c else ~has_classic) &
            (has_rapid if r else ~has_rapid) &
            (has_blitz if b else ~has_blitz)
            for c, r, b in PLAYER_PROFILE_RULES.keys()
        ]
        df_feat["player_profile"] = pd.Categorical(
            np.select(condiciones_perfil, self.ORDERED_PROFILE, default="sin_elo"),
            categories=self.ORDERED_PROFILE,
            ordered=True,
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
