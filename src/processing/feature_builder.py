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

    ORDERED_PROFILE: List[str] = [
        "completo",
        "especialista_clasico",
        "especialista_rapido",
        "especialista_blitz",
        "clasico_rapido",
        "clasico_blitz",
        "rapido_blitz"]

    def __init__(self, reference_year: int = None):
        self.reference_year = reference_year or datetime.now().year

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula edad, actividad y categorías oficiales FIDE."""
        df_feat = df.copy()
        logger.info(f"Generando features con año de referencia {self.reference_year}...")

        if "flag" in df_feat.columns:
            flag_str = df_feat["flag"].fillna("").astype(str).str.strip()
            df_feat["es_activo"] = ~flag_str.isin(["i", "wi"])
            df_feat = df_feat.drop(columns=["flag"])
        else:
            df_feat["es_activo"] = True

        df_feat["edad"] = self.reference_year - df_feat["birthday"].astype(int)

        condiciones_edad = [
            (df_feat["edad"] > 0) & (df_feat["edad"] <= 8), # Sub 8
            (df_feat["edad"] > 8) & (df_feat["edad"] <= 10), # Sub 10
            (df_feat["edad"] > 10) & (df_feat["edad"] <= 12), # Sub 12
            (df_feat["edad"] > 12) & (df_feat["edad"] <= 14), # Sub 14
            (df_feat["edad"] > 14) & (df_feat["edad"] <= 16), # Sub 16
            (df_feat["edad"] > 16) & (df_feat["edad"] <= 18), # Sub 18
            (df_feat["edad"] > 18) & (df_feat["edad"] <= 20), # Sub 20
            (df_feat["edad"] > 20), # Absoluto
        ]

        has_classic = df_feat["rating"].notna() if "rating" in df_feat.columns else pd.Series(False, index=df_feat.index)
        has_rapid = df_feat["rapid_rating"].notna() if "rapid_rating" in df_feat.columns else pd.Series(False, index=df_feat.index)
        has_blitz = df_feat["blitz_rating"].notna() if "blitz_rating" in df_feat.columns else pd.Series(False, index=df_feat.index)

        condiciones_perfil = [
            has_classic & has_rapid & has_blitz,          # completo
            has_classic & ~has_rapid & ~has_blitz,        # especialista_clasico
            ~has_classic & has_rapid & ~has_blitz,        # especialista_rapido
            ~has_classic & ~has_rapid & has_blitz,        # especialista_blitz
            has_classic & has_rapid & ~has_blitz,         # clasico_rapido
            has_classic & ~has_rapid & has_blitz,         # clasico_blitz
            ~has_classic & has_rapid & has_blitz,         # rapido_blitz
        ]

        df_feat["player_profile"] = np.select(
            condiciones_perfil,
            self.ORDERED_PROFILE,
            default="sin_elo"
        )

        df_feat["player_profile"] = pd.Categorical(
            df_feat["player_profile"],
            categories=self.ORDERED_PROFILE,
            ordered=True
        )


        df_feat["categoria"] = np.select(
            condiciones_edad,
            self.ORDERED_CATEGORIES,
            default="sin_categoría"
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
