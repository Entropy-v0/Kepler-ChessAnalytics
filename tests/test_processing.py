"""
tests/test_processing.py
========================
Pruebas unitarias para la fase de procesamiento (Cleaner y FeatureBuilder).
"""

import pandas as pd
import numpy as np
from src.processing.cleaner import DataCleaner
from src.processing.feature_builder import FeatureBuilder


def test_cleaner_filters_invalid_records():
    cleaner = DataCleaner()
    raw_data = pd.DataFrame([
        {"fideid": "1", "name": "Player 1", "rating": 1500, "rapid_rating": None, "blitz_rating": None, "birthday": 1990, "flag": ""},
        {"fideid": "2", "name": "Player 2", "rating": 0, "rapid_rating": 0, "blitz_rating": None, "birthday": 1990, "flag": ""},
        {"fideid": "3", "name": "Player 3", "rating": 1600, "rapid_rating": None, "blitz_rating": None, "birthday": None, "flag": ""},
        {"fideid": "4", "name": "Player 4", "rating": 1700, "rapid_rating": None, "blitz_rating": None, "birthday": 1850, "flag": ""},
        {"fideid": "1", "name": "Player 1 Dup", "rating": 1500, "rapid_rating": None, "blitz_rating": None, "birthday": 1990, "flag": ""},
    ])

    cleaned = cleaner.clean(raw_data)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["fideid"] == "1"
    assert cleaned.iloc[0]["title"] == "nt"


def test_feature_builder_categories_and_split():
    fb = FeatureBuilder(reference_year=2026)
    clean_data = pd.DataFrame([
        {"fideid": "1", "birthday": 2020, "flag": "", "rating": 1200},   # edad = 6 -> Sub 8, activo
        {"fideid": "2", "birthday": 2017, "flag": "", "rating": 1300},   # edad = 9 -> Sub 10, activo
        {"fideid": "3", "birthday": 2011, "flag": "", "rating": 1400},   # edad = 15 -> Sub 16, activo
        {"fideid": "4", "birthday": 2000, "flag": "i", "rating": 2000},  # edad = 26 -> Absoluta, inactivo
        {"fideid": "5", "birthday": 1925, "flag": "", "rating": 1800},   # edad = 101 -> Absoluta, activo pero edad > 95
    ])

    enriched = fb.build_features(clean_data)
    assert enriched.loc[enriched["fideid"] == "1", "categoria"].values[0] == "Sub 8"
    assert enriched.loc[enriched["fideid"] == "2", "categoria"].values[0] == "Sub 10"
    assert enriched.loc[enriched["fideid"] == "3", "categoria"].values[0] == "Sub 16"
    assert enriched.loc[enriched["fideid"] == "4", "categoria"].values[0] == "Absoluta"
    assert enriched.loc[enriched["fideid"] == "4", "es_activo"].values[0] == False
    assert "flag" not in enriched.columns

    all_df, active_df = fb.split_datasets(enriched)
    assert len(all_df) == 5
    assert len(active_df) == 3
    assert set(active_df["fideid"]) == {"1", "2", "3"}


def test_feature_builder_player_profile():
    fb = FeatureBuilder(reference_year=2026)
    data = pd.DataFrame([
        {"fideid": "1", "birthday": 2000, "flag": "", "rating": 2100, "rapid_rating": 2050, "blitz_rating": 2000},
        # 2. Especialista clásico: solo clásico
        {"fideid": "2", "birthday": 2000, "flag": "", "rating": 1900, "rapid_rating": np.nan, "blitz_rating": None},
        # 3. Especialista rápido: solo rápido
        {"fideid": "3", "birthday": 2000, "flag": "", "rating": np.nan, "rapid_rating": 1850, "blitz_rating": np.nan},
        # 4. Especialista blitz: solo blitz
        {"fideid": "4", "birthday": 2000, "flag": "", "rating": None, "rapid_rating": None, "blitz_rating": 1700},
        # 5. Clásico + Rápido
        {"fideid": "5", "birthday": 2000, "flag": "", "rating": 2200, "rapid_rating": 2150, "blitz_rating": None},
        # 6. Clásico + Blitz
        {"fideid": "6", "birthday": 2000, "flag": "", "rating": 2300, "rapid_rating": np.nan, "blitz_rating": 2250},
        # 7. Rápido + Blitz
        {"fideid": "7", "birthday": 2000, "flag": "", "rating": None, "rapid_rating": 1600, "blitz_rating": 1650},
    ])

    enriched = fb.build_features(data)

    # Validar la asignación de cada uno de los 7 perfiles
    assert enriched.loc[enriched["fideid"] == "1", "player_profile"].values[0] == "completo"
    assert enriched.loc[enriched["fideid"] == "2", "player_profile"].values[0] == "especialista_clasico"
    assert enriched.loc[enriched["fideid"] == "3", "player_profile"].values[0] == "especialista_rapido"
    assert enriched.loc[enriched["fideid"] == "4", "player_profile"].values[0] == "especialista_blitz"
    assert enriched.loc[enriched["fideid"] == "5", "player_profile"].values[0] == "clasico_rapido"
    assert enriched.loc[enriched["fideid"] == "6", "player_profile"].values[0] == "clasico_blitz"
    assert enriched.loc[enriched["fideid"] == "7", "player_profile"].values[0] == "rapido_blitz"

    # Validar tipo categórico ordenado y categorías oficiales
    assert isinstance(enriched["player_profile"].dtype, pd.CategoricalDtype)
    assert enriched["player_profile"].dtype.ordered is True
    assert list(enriched["player_profile"].dtype.categories) == fb.ORDERED_PROFILE


def test_constants_rules_consistency():
    from src.config.constants import (
        AGE_CATEGORY_RULES,
        CAT_ORDER,
        PLAYER_PROFILE_RULES,
        PRO_ORDER,
    )
    fb = FeatureBuilder()
    assert list(AGE_CATEGORY_RULES.values()) == CAT_ORDER
    assert CAT_ORDER == fb.ORDERED_CATEGORIES
    assert list(PLAYER_PROFILE_RULES.values()) == PRO_ORDER
    assert PRO_ORDER == fb.ORDERED_PROFILE

    for (min_age, max_age), cat_name in AGE_CATEGORY_RULES.items():
        assert isinstance(min_age, int)
        assert max_age is None or isinstance(max_age, int)
        assert isinstance(cat_name, str)

    for (c, r, b), prof_name in PLAYER_PROFILE_RULES.items():
        assert isinstance(c, bool)
        assert isinstance(r, bool)
        assert isinstance(b, bool)
        assert isinstance(prof_name, str)


