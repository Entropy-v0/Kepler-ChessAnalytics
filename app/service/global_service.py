"""
app/service/global_service.py
==============================
Servicio de datos analíticos para la página 01 — Panorama Global.
Consume los Data Marts precalculados (Capa Oro).
"""

from typing import Any, Dict, Tuple
import pandas as pd

from service.data_loader import (
    load_global_kpis_mart,
    load_panorama_global_mart,
)


def get_global_kpis() -> Dict[str, Any]:
    """Retorna las métricas globales principales (total jugadores, activos, países)."""
    df_kpis = load_global_kpis_mart()
    return {
        "total_players": int(df_kpis.iloc[0]["total_players"]),
        "active_players": int(df_kpis.iloc[0]["active_players"]),
        "total_countries": int(df_kpis.iloc[0]["total_countries"]),
    }


def get_top_federations_summary(top_n: int = 15) -> Tuple[pd.DataFrame, int]:
    """Calcula el ranking y % acumulado de las Top N federaciones."""
    df_panorama = load_panorama_global_mart()
    cols = ["#", "Federación", "Jugadores", "% del mundial", "Acumulado %"]
    fed_counts = df_panorama.head(top_n)[cols].copy()
    return fed_counts, top_n


def get_world_map_data() -> pd.DataFrame:
    """Prepara y mapea los datos de países para el mapa de coropletas."""
    df_panorama = load_panorama_global_mart()
    cols = ["country", "Jugadores", "log_jugadores", "Jugadores_fmt"]
    return df_panorama[cols].copy()
