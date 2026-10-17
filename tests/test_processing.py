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
    cleaner = DataCleaner(reference_year=2026)
    raw_data = pd.DataFrame([
        {"fideid": "1", "name": "Player 1", "country": "VEN", "rating": 1500, "rapid_rating": None, "blitz_rating": None, "birthday": 1990, "flag": ""},
        {"fideid": "2", "name": "Player 2", "country": "COL", "rating": 0, "rapid_rating": 0, "blitz_rating": None, "birthday": 1990, "flag": ""},
        {"fideid": "3", "name": "Player 3", "country": "ARG", "rating": 1600, "rapid_rating": None, "blitz_rating": None, "birthday": None, "flag": ""},
        {"fideid": "4", "name": "Player 4", "country": "ESP", "rating": 1700, "rapid_rating": None, "blitz_rating": None, "birthday": 1850, "flag": ""},
        {"fideid": "5", "name": "Player 5", "country": "USA", "rating": 1800, "rapid_rating": None, "blitz_rating": None, "birthday": 2026, "flag": ""},
        {"fideid": "1", "name": "Player 1 Dup", "country": "VEN", "rating": 1500, "rapid_rating": None, "blitz_rating": None, "birthday": 1990, "flag": ""},
    ])

    result = cleaner.clean(raw_data)
    assert result.input_rows == 6
    assert len(result.clean) == 1
    assert len(result.rejected) == 5
    assert result.clean.iloc[0]["fideid"] == "1"
    assert result.clean.iloc[0]["title"] == "nt"
    assert "w_title" not in result.clean.columns
    assert result.rejections_by_rule() == {
        "sin_rating": 1,
        "sin_birthday": 1,
        "birthday_anomalo": 1,
        "birthday_futuro": 1,
        "duplicado": 1,
    }


def test_cleaner_title_fusion_and_sex_correction():
    cleaner = DataCleaner(reference_year=2026)
    raw_data = pd.DataFrame([
        # Caso 1: title='nt', w_title='WFM' -> title='WFM'
        {"fideid": "10", "name": "P1", "country": "VEN", "sex": "F", "title": None, "w_title": "WFM", "rating": 1900, "rapid_rating": 0, "blitz_rating": 0, "birthday": 2000},
        # Caso 2: title='FM', w_title='WGM' -> WGM > FM por jerarquia
        {"fideid": "20", "name": "P2", "country": "VEN", "sex": "F", "title": "FM", "w_title": "WGM", "rating": 2300, "rapid_rating": 0, "blitz_rating": 0, "birthday": 1998},
        # Caso 3: title='IM', w_title='WGM' -> IM > WGM por jerarquia
        {"fideid": "30", "name": "P3", "country": "IND", "sex": "F", "title": "IM", "w_title": "WGM", "rating": 2410, "rapid_rating": 0, "blitz_rating": 0, "birthday": 1995},
        # Caso 4: anomalia sex='M' con titulo femenino -> corrige sex='F'
        {"fideid": "40", "name": "P4", "country": "IND", "sex": "M", "title": "WCM", "w_title": "WCM", "rating": 1980, "rapid_rating": 0, "blitz_rating": 0, "birthday": 1985},
    ])

    result = cleaner.clean(raw_data)
    clean = result.clean.set_index("fideid")
    assert clean.loc["10", "title"] == "WFM"
    assert clean.loc["20", "title"] == "WGM"
    assert clean.loc["30", "title"] == "IM"
    assert clean.loc["40", "sex"] == "F"
    assert "w_title" not in clean.columns



def test_feature_builder_categories_and_split():
    fb = FeatureBuilder(reference_year=2026)
    clean_data = pd.DataFrame([
        {"fideid": "1", "birthday": 2020, "flag": "", "rating": 1200, "games": 5, "rapid_games": 0, "blitz_games": 0},   # edad = 6 -> Sub 8, activo
        {"fideid": "2", "birthday": 2017, "flag": "", "rating": 1300, "games": 0, "rapid_games": 7, "blitz_games": 2},   # edad = 9 -> Sub 10, activo
        {"fideid": "3", "birthday": 2011, "flag": "", "rating": 1400, "games": 0, "rapid_games": 0, "blitz_games": 0},   # edad = 15 -> Sub 16, activo
        {"fideid": "4", "birthday": 2000, "flag": "i", "rating": 2000, "games": 0, "rapid_games": 0, "blitz_games": 0},  # edad = 26 -> Absoluta, inactivo
        {"fideid": "5", "birthday": 1925, "flag": "", "rating": 1800, "games": 0, "rapid_games": 0, "blitz_games": 0},   # edad = 101 -> Absoluta, activo pero edad > 95
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
    from src.config.constants import PRO_ORDER
    assert isinstance(enriched["player_profile"].dtype, pd.CategoricalDtype)
    assert enriched["player_profile"].dtype.ordered is True
    assert list(enriched["player_profile"].dtype.categories) == PRO_ORDER


def test_constants_rules_consistency():
    from src.config.constants import (
        AGE_CATEGORY_RULES,
        CAT_ORDER,
        MODALIDADES_MAP,
        PLAYER_PROFILE_RULES,
        PRO_ORDER,
        RATING_COLS,
        TITLE_ORDER,
        TITLE_WOMAN,
        TITLES_ELITE,
        YOUTH_CATS,
    )
    assert list(AGE_CATEGORY_RULES.values()) == CAT_ORDER
    assert YOUTH_CATS == [c for c in CAT_ORDER if c != "Absoluta"]
    assert list(PLAYER_PROFILE_RULES.values()) == PRO_ORDER
    assert tuple(MODALIDADES_MAP.keys()) == RATING_COLS
    assert TITLE_WOMAN == ["WGM", "WIM", "WFM", "WCM"]
    assert TITLE_ORDER == ["nt"] + TITLES_ELITE[::-1]

    for (min_age, max_age), cat_name in AGE_CATEGORY_RULES.items():
        assert isinstance(min_age, int)
        assert max_age is None or isinstance(max_age, int)
        assert isinstance(cat_name, str)

    for (c, r, b), prof_name in PLAYER_PROFILE_RULES.items():
        assert isinstance(c, bool)
        assert isinstance(r, bool)
        assert isinstance(b, bool)
        assert isinstance(prof_name, str)


def test_demografia_and_rankings_analytics_engines():
    from src.analytics import Demografia, Rankings

    cleaner = DataCleaner(reference_year=2026)
    fb = FeatureBuilder(reference_year=2026)

    raw_data = pd.DataFrame([
        {"fideid": "1", "name": "Ven GM", "country": "VEN", "sex": "M", "title": "GM", "w_title": None, "rating": 2550, "rapid_rating": 2500, "blitz_rating": 2520, "games": 9, "rapid_games": 5, "blitz_games": 0, "birthday": 1995, "flag": ""},
        {"fideid": "2", "name": "Ven Youth F", "country": "VEN", "sex": "F", "title": None, "w_title": "WFM", "rating": 1800, "rapid_rating": 1950, "blitz_rating": 1900, "games": 0, "rapid_games": 7, "blitz_games": 9, "birthday": 2012, "flag": ""},
        {"fideid": "3", "name": "Ven Rapid Spec", "country": "VEN", "sex": "M", "title": None, "w_title": None, "rating": 0, "rapid_rating": 1700, "blitz_rating": 0, "games": 0, "rapid_games": 0, "blitz_games": 0, "birthday": 2010, "flag": ""},
        {"fideid": "4", "name": "Ven Adult F", "country": "VEN", "sex": "F", "title": None, "w_title": None, "rating": 1600, "rapid_rating": 0, "blitz_rating": 0, "games": 0, "rapid_games": 0, "blitz_games": 0, "birthday": 1998, "flag": "wi"},
        {"fideid": "5", "name": "Col IM", "country": "COL", "sex": "M", "title": "IM", "w_title": None, "rating": 2420, "rapid_rating": 2380, "blitz_rating": 2400, "games": 9, "rapid_games": 0, "blitz_games": 0, "birthday": 1992, "flag": ""},
        {"fideid": "6", "name": "Col Youth M", "country": "COL", "sex": "M", "title": None, "w_title": None, "rating": 1650, "rapid_rating": 1720, "blitz_rating": 1680, "games": 0, "rapid_games": 9, "blitz_games": 0, "birthday": 2012, "flag": ""},
    ])

    clean_res = cleaner.clean(raw_data)
    df_all = fb.build_features(clean_res.clean)

    # 1. Estudio Demográfico general por país y global (Demografia)
    ven_demo = Demografia(df_all, "ven")
    df_kpis = ven_demo.kpis_demograficos()
    assert list(df_kpis.columns) == ["cantidad", "porcentaje"]
    assert df_kpis.loc["registrados", "cantidad"] == 4
    assert df_kpis.loc["hombres", "cantidad"] == 2
    assert df_kpis.loc["mujeres", "cantidad"] == 2
    assert df_kpis.loc["titulados", "cantidad"] == 2

    global_demo = Demografia(df_all)
    df_kpis_global = global_demo.kpis_demograficos()
    assert df_kpis_global.loc["registrados", "cantidad"] == 6

    demo_df = ven_demo.resumen_demografico()
    assert len(demo_df) == 8
    abs_row = demo_df.loc[demo_df["categoria"] == "Absoluta"].iloc[0]
    assert abs_row["registrados"] == 2

    prof_df = ven_demo.resumen_perfiles().set_index("player_profile")
    assert prof_df.loc["completo", "jugadores"] == 2
    assert prof_df.loc["especialista_rapido", "jugadores"] == 1

    titles_df = ven_demo.resumen_titulos().set_index("title")
    assert titles_df.loc["GM", "total"] == 1
    assert titles_df.loc["WFM", "F"] == 1

    comp_feds = Demografia.comparar_federaciones(df_all, ["VEN", "COL"])
    assert list(comp_feds["country"]) == ["VEN", "COL"]
    assert len(comp_feds) == 2

    # 2. Estudio de Rankings y Elo por país y global (Rankings)
    ven_rank = Rankings(df_all, "ven")
    elo_df = ven_rank.comparativa_elo().set_index("columna")
    assert elo_df.loc["rating", "jugadores"] == 3
    assert elo_df.loc["rapid_rating", "jugadores"] == 3

    global_rank = Rankings(df_all)
    assert len(global_rank.ranking_y_percentiles(modalidad="rating")) == 5

    curvas_df = ven_rank.curvas_por_categoria()
    assert len(curvas_df) == 8

    corr_df = ven_rank.correlacion_ritmos(solo_completos=True)
    assert list(corr_df.columns) == ["rating", "rapid_rating", "blitz_rating"]

    rank_df = ven_rank.ranking_y_percentiles(modalidad="rating")
    assert len(rank_df) == 3
    assert rank_df.iloc[0]["fideid"] == "1"
    assert rank_df.loc[rank_df["fideid"] == "2", "gap_rapido_clasico"].iloc[0] == 150.0


def test_player_model_and_games_normalization():
    from src.models.player import FidePlayer

    p = FidePlayer(
        fideid=4400018,
        name="Zapata, Alonso",
        country="COL",
        sex="M",
        title="GM",
        rating=2450,
        games="9",
        rapid_games=0,
        blitz_games=None,
        birthday=1958,
        snapshot_date="2026-10-01",
    )
    assert isinstance(p.fideid, str)
    assert p.fideid == "4400018"
    assert p.games == 9
    assert p.rapid_games == 0
    assert p.blitz_games is None

    cleaner = DataCleaner(reference_year=2026)
    raw_df = pd.DataFrame([p.model_dump()])
    res = cleaner.clean(raw_df)
    clean_df = res.clean
    assert clean_df["fideid"].iloc[0] == "4400018"
    assert clean_df["games"].dtype == "int16"
    assert clean_df["rapid_games"].dtype == "int16"
    assert clean_df["blitz_games"].dtype == "int16"
    assert clean_df["games"].iloc[0] == 9
    assert clean_df["rapid_games"].iloc[0] == 0
    assert clean_df["blitz_games"].iloc[0] == 0


