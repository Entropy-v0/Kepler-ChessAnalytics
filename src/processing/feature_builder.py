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
    GAMES_COLS,
    INACTIVE_FLAGS,
    MAX_ACTIVE_AGE,
    PLAYER_PROFILE_RULES,
    PRO_ORDER,
)


class FeatureBuilder:
    """Clase encargada de enriquecer el padrón FIDE con variables derivadas y segmentación."""

    def __init__(self, reference_year: int = None):
        self.reference_year = reference_year or datetime.now().year

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula edad, actividad FIDE corregida, actividad mensual y categorías oficiales FIDE."""
        df_feat = df.copy()
        logger.info(f"Generando features con año de referencia {self.reference_year}...")

        # 1. Bandera de actividad oficial FIDE y partidas del mes
        if "flag" in df_feat.columns:
            flag_str = df_feat["flag"].fillna("").astype(str).str.strip()
            df_feat["es_activo"] = ~flag_str.isin(INACTIVE_FLAGS)
            df_feat = df_feat.drop(columns=["flag"])
        elif "es_activo" not in df_feat.columns:
            df_feat["es_activo"] = True

        for g_col in GAMES_COLS:
            if g_col not in df_feat.columns:
                df_feat[g_col] = np.int16(0)
            else:
                df_feat[g_col] = pd.to_numeric(df_feat[g_col], errors="coerce").fillna(0).astype("int16")

        # 2. Edad federativa y Categorías por edad
        df_feat["edad"] = self.reference_year - df_feat["birthday"].astype(int)
        edad = df_feat["edad"]

        condiciones_edad = [
            (edad > min_age) if max_age is None else (edad > min_age) & (edad <= max_age)
            for min_age, max_age in AGE_CATEGORY_RULES.keys()
        ]

        df_feat["categoria"] = pd.Categorical(
            np.select(condiciones_edad, CAT_ORDER, default="sin_categoría"),
            categories=CAT_ORDER,
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
            np.select(condiciones_perfil, PRO_ORDER, default="sin_elo"),
            categories=PRO_ORDER,
            ordered=True,
        )

        logger.success(f"Features construidas exitosamente ({len(df_feat):,} registros).")
        return df_feat

    def split_datasets(self, df_enriched: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Segmenta en:
        1. df_all: Padrón total limpio.
        2. df_active: Padrón de activos (flag != 'i'/'wi') con edad <= MAX_ACTIVE_AGE años.
        """
        df_all = df_enriched.copy()

        df_active = df_enriched[
            df_enriched["es_activo"] & (df_enriched["edad"] <= MAX_ACTIVE_AGE)
        ].copy()

        logger.info(f"Padrón general: {len(df_all):,} registros | Padrón activo: {len(df_active):,} registros.")
        return df_all, df_active


