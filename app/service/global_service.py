"""
app/service/global_service.py
==============================
Servicio de datos analíticos para la página 01 — Panorama Global.
"""

import math
from typing import Any, Dict, Tuple
import pandas as pd

from components.theme import FIDE_TO_ISO3
from service.data_loader import load_active_players, load_all_players


def get_global_kpis() -> Dict[str, Any]:
    """Retorna las métricas globales principales (total jugadores, activos, países)."""
    df_all = load_all_players()
    df_active = load_active_players()
    return {
        "total_players": len(df_all),
        "active_players": len(df_active),
        "total_countries": df_all["country"].nunique(),
    }


def get_top_federations_summary(top_n: int = 15) -> Tuple[pd.DataFrame, int]:
    """Calcula el ranking y % acumulado de las Top N federaciones."""
    df_all = load_all_players()
    total_players = len(df_all)

    fed_counts = df_all["country"].value_counts().head(top_n).reset_index()
    fed_counts.columns = ["Federación", "Jugadores"]
    fed_counts["% del mundial"] = (fed_counts["Jugadores"] / total_players * 100).round(1)
    fed_counts["Acumulado %"] = fed_counts["% del mundial"].cumsum().round(1)
    fed_counts.insert(0, "#", range(1, len(fed_counts) + 1))

    return fed_counts, top_n


def get_world_map_data() -> pd.DataFrame:
    """Prepara y mapea los datos de países para el mapa de coropletas."""
    df_all = load_all_players()
    map_raw = df_all["country"].value_counts().reset_index()
    map_raw.columns = ["country_fide", "Jugadores"]
    map_raw["iso3"] = map_raw["country_fide"].map(lambda c: FIDE_TO_ISO3.get(c, c))

    map_data = (
        map_raw.groupby("iso3", as_index=False)["Jugadores"]
        .sum()
        .rename(columns={"iso3": "country"})
    )
    map_data["log_jugadores"] = map_data["Jugadores"].apply(
        lambda x: round(math.log10(x), 3) if x > 0 else 0
    )
    map_data["Jugadores_fmt"] = map_data["Jugadores"].apply(lambda x: f"{x:,}")

    return map_data
