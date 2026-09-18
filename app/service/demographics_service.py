"""
app/service/demographics_service.py
===================================
Servicio de datos analíticos para la página 03 — Demografía y Género.
"""

from typing import Any, Dict, Tuple
import pandas as pd

from components.theme import CAT_ORDER
from service.data_loader import load_active_players


def get_demographic_kpis() -> Dict[str, Any]:
    """Calcula los KPIs clave de género, juvenil vs adulto."""
    df = load_active_players()
    total = len(df)
    n_m = int((df["sex"] == "M").sum())
    n_f = int((df["sex"] == "F").sum())
    pct_m = n_m / total * 100
    pct_f = n_f / total * 100

    df_youth = df[df["categoria"] != "Absoluta"]
    n_youth = len(df_youth)
    pct_youth = n_youth / total * 100
    pct_f_youth = (df_youth["sex"] == "F").mean() * 100

    df_adult = df[df["categoria"] == "Absoluta"]
    pct_f_adult = (df_adult["sex"] == "F").mean() * 100

    return {
        "n_m": n_m,
        "n_f": n_f,
        "pct_m": pct_m,
        "pct_f": pct_f,
        "n_youth": n_youth,
        "pct_youth": pct_youth,
        "pct_f_youth": pct_f_youth,
        "pct_f_adult": pct_f_adult,
        "drop_pp": pct_f_youth - pct_f_adult,
    }


def get_top_federations_gender_ratio(top_n: int = 20) -> pd.DataFrame:
    """Calcula la proporción de género en el Top N federaciones por volumen."""
    df = load_active_players()
    top_feds = df["country"].value_counts().head(top_n).index.tolist()
    fed_sex = (
        df[df["country"].isin(top_feds)]
        .groupby(["country", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    fed_sex.columns.name = None
    fed_sex["total"] = fed_sex["M"] + fed_sex["F"]
    fed_sex["pct_F"] = (fed_sex["F"] / fed_sex["total"] * 100).round(1)
    fed_sex["pct_M"] = (fed_sex["M"] / fed_sex["total"] * 100).round(1)
    return fed_sex.sort_values("total", ascending=True)


def get_fide_categories_gender() -> pd.DataFrame:
    """Estructura poblacional por Categorías FIDE."""
    df = load_active_players()
    cat_df = (
        df.groupby(["categoria", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(CAT_ORDER)
        .reset_index()
    )
    cat_df.columns.name = None
    cat_df["total"] = cat_df["M"] + cat_df["F"]
    cat_df["pct_F"] = (cat_df["F"] / cat_df["total"] * 100).round(1)
    cat_df["pct_M"] = (cat_df["M"] / cat_df["total"] * 100).round(1)
    return cat_df


def get_age_quinquennial_pyramid() -> pd.DataFrame:
    """Pirámide de población por grupos de edad quinquenales."""
    df = load_active_players()
    age_bins = list(range(0, 100, 5)) + [100]
    age_labels = [f"{i}–{i+4}" for i in range(0, 95, 5)] + ["95+"]

    df_copy = df.copy()
    df_copy["age_bin"] = pd.cut(df_copy["edad"], bins=age_bins, labels=age_labels, right=False)

    pyramid_age = (
        df_copy.groupby(["age_bin", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    pyramid_age.columns = ["age_bin", "F", "M"]
    pyramid_age = pyramid_age[pyramid_age["age_bin"].notna()].copy()
    pyramid_age["age_bin"] = pyramid_age["age_bin"].astype(str)
    return pyramid_age


def get_gender_parity_top_countries(min_players: int = 500, top_n: int = 12) -> pd.DataFrame:
    """Federaciones con al menos N jugadores con mayor cuota de participación femenina."""
    df = load_active_players()
    fed_all = (
        df.groupby(["country", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    fed_all.columns.name = None
    fed_all["total"] = fed_all["M"] + fed_all["F"]
    fed_all["pct_F"] = (fed_all["F"] / fed_all["total"] * 100).round(1)

    best_parity = (
        fed_all[fed_all["total"] >= min_players]
        .sort_values("pct_F", ascending=False)
        .head(top_n)
        .sort_values("pct_F", ascending=True)
    )
    return best_parity
