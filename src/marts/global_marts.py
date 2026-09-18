"""
src/marts/global_marts.py
==========================
Generador de Data Marts para Panorama Global (Página 01).
Precalcula KPIs, Top Federaciones y Mapa Mundial Coroplético.
"""

import math
from pathlib import Path
import pandas as pd
from loguru import logger

from src.config.constants import FIDE_TO_ISO3


def build_global_marts(df_all: pd.DataFrame, df_active: pd.DataFrame, output_dir: Path) -> None:
    """Genera mart_kpis_globales.parquet y mart_panorama_global.parquet."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generando Data Marts: Panorama Global...")

    total_players = len(df_all)
    active_players = len(df_active)
    total_countries = int(df_all["country"].nunique())

    # 1. Mart de KPIs Globales (1 sola fila)
    kpis_df = pd.DataFrame([{
        "total_players": total_players,
        "active_players": active_players,
        "total_countries": total_countries,
    }])
    kpis_path = output_dir / "mart_kpis_globales.parquet"
    kpis_df.to_parquet(kpis_path, index=False)
    logger.success(f"Guardado {kpis_path.name} ({kpis_path.stat().st_size:,} bytes)")

    # 2. Mart de Federaciones y Mapa Mundial
    fed_counts = df_all["country"].value_counts().reset_index()
    fed_counts.columns = ["country_fide", "Jugadores"]

    fed_counts["% del mundial"] = (fed_counts["Jugadores"] / total_players * 100).round(1)
    fed_counts["Acumulado %"] = fed_counts["% del mundial"].cumsum().round(1)
    fed_counts["#"] = range(1, len(fed_counts) + 1)
    fed_counts["Federación"] = fed_counts["country_fide"]

    # Mapeo a código ISO-3 para coropletas
    fed_counts["iso3"] = fed_counts["country_fide"].map(lambda c: FIDE_TO_ISO3.get(c, c))
    fed_counts["country"] = fed_counts["iso3"]
    fed_counts["log_jugadores"] = fed_counts["Jugadores"].apply(
        lambda x: round(math.log10(x), 3) if x > 0 else 0
    )
    fed_counts["Jugadores_fmt"] = fed_counts["Jugadores"].apply(lambda x: f"{x:,}")

    panorama_path = output_dir / "mart_panorama_global.parquet"
    fed_counts.to_parquet(panorama_path, index=False)
    logger.success(f"Guardado {panorama_path.name} ({panorama_path.stat().st_size:,} bytes)")
