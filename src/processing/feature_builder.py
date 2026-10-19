"""
src/processing/feature_builder.py
==================================
Módulo de ingeniería de características para el padrón FIDE.
Calcula edad federativa, banderas de actividad y categorías formativas.
"""

from datetime import datetime
from typing import Optional
import numpy as np
import pandas as pd
from loguru import logger

from src.config.constants import (
    AGE_CATEGORY_RULES,
    CAT_ORDER,
    GAMES_COLS,
    PLAYER_PROFILE_RULES,
    PRO_ORDER,
)


class FeatureBuilder:
    """Clase encargada de enriquecer el padrón FIDE con variables derivadas."""

    def __init__(self, reference_year: Optional[int] = None):
        self.reference_year = reference_year or datetime.now().year

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula partidas totales del mes, actividad mensual, edad, categorías y perfil de ritmo."""
        df_feat = df.copy()
        logger.info(f"Generando features con año de referencia {self.reference_year}...")

        if "flag" in df_feat.columns:
            df_feat = df_feat.drop(columns=["flag"])

        # 1. Volumen de partidas del mes y actividad mensual (al menos 1 partida evaluada)
        for g_col in GAMES_COLS:
            if g_col not in df_feat.columns:
                df_feat[g_col] = np.int16(0)
            else:
                df_feat[g_col] = pd.to_numeric(df_feat[g_col], errors="coerce").fillna(0).astype("int16")

        df_feat["total_games"] = (
            df_feat["games"] + df_feat["rapid_games"] + df_feat["blitz_games"]
        ).astype("int16")
        df_feat["activo_mes"] = df_feat["total_games"] > 0

        # 2. Edad federativa y Categorías por edad
        df_feat["edad"] = (self.reference_year - df_feat["birthday"].astype(int)).astype("int16")
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

        n_activos_mes = int(df_feat["activo_mes"].sum())
        logger.success(
            f"Features construidas exitosamente ({len(df_feat):,} registros | activos en el mes: {n_activos_mes:,})."
        )
        return df_feat
