"""
app/service/demographics_service.py
===================================
Servicio de datos analíticos para la página 03 — Demografía y Género.
Consume los Data Marts precalculados (Capa Oro).
"""

from typing import Any, Dict
import pandas as pd

from service.data_loader import (
    load_demografia_kpis_mart,
    load_demografia_federaciones_mart,
    load_demografia_categorias_mart,
    load_demografia_piramide_mart,
    load_demografia_paridad_mart,
)


def get_demographic_kpis() -> Dict[str, Any]:
    """Calcula los KPIs clave de género, juvenil vs adulto."""
    df_kpis = load_demografia_kpis_mart()
    row = df_kpis.iloc[0]
    return {
        "n_m": int(row["n_m"]),
        "n_f": int(row["n_f"]),
        "pct_m": float(row["pct_m"]),
        "pct_f": float(row["pct_f"]),
        "n_youth": int(row["n_youth"]),
        "pct_youth": float(row["pct_youth"]),
        "pct_f_youth": float(row["pct_f_youth"]),
        "pct_f_adult": float(row["pct_f_adult"]),
        "drop_pp": float(row["drop_pp"]),
    }


def get_top_federations_gender_ratio(top_n: int = 20) -> pd.DataFrame:
    """Calcula la proporción de género en el Top N federaciones por volumen."""
    df_feds = load_demografia_federaciones_mart()
    return df_feds.tail(top_n).sort_values("total", ascending=True).copy()


def get_fide_categories_gender() -> pd.DataFrame:
    """Estructura poblacional por Categorías FIDE."""
    return load_demografia_categorias_mart().copy()


def get_age_quinquennial_pyramid() -> pd.DataFrame:
    """Pirámide de población por grupos de edad quinquenales."""
    return load_demografia_piramide_mart().copy()


def get_gender_parity_top_countries(min_players: int = 500, top_n: int = 12) -> pd.DataFrame:
    """Federaciones con al menos N jugadores con mayor cuota de participación femenina."""
    df_paridad = load_demografia_paridad_mart()
    filtered = df_paridad[df_paridad["total"] >= min_players].head(top_n)
    return filtered.sort_values("pct_F", ascending=True).copy()
