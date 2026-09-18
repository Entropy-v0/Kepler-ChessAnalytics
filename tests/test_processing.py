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

    all_df, active_df = fb.split_datasets(enriched)
    assert len(all_df) == 5
    assert len(active_df) == 3
    assert set(active_df["fideid"]) == {"1", "2", "3"}
