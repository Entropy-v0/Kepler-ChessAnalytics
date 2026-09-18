"""
app/service/youth_service.py
=============================
Servicio de datos analíticos para la página 04 — Cohortes Juveniles.
Consume los Data Marts precalculados (Capa Oro).
"""

from typing import Any, Dict, Tuple
import pandas as pd

from service.data_loader import (
    load_youth_kpis_mart,
    load_youth_categorias_mart,
    load_youth_elo_curves_mart,
    load_youth_canteras_matriz_mart,
)


def get_youth_kpis() -> Dict[str, Any]:
    """Calcula las métricas principales del ajedrez juvenil mundial."""
    df_kpis = load_youth_kpis_mart()
    row = df_kpis.iloc[0]
    return {
        "total_youth": int(row["total_youth"]),
        "pct_youth_global": float(row["pct_youth_global"]),
        "peak_cat": str(row["peak_cat"]),
        "peak_count": int(row["peak_count"]),
        "elo_diff": int(row["elo_diff"]),
    }


def get_youth_categories_breakdown() -> pd.DataFrame:
    """Retorna el desglose por categoría juvenil y sexo."""
    return load_youth_categorias_mart().copy()


def get_youth_elo_curves_data() -> pd.DataFrame:
    """Calcula las curvas de desarrollo de medianas y percentiles de Elo por cohorte."""
    return load_youth_elo_curves_mart().copy()


def get_youth_canteras_summary() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula el Top de canteras por cuota % y por volumen absoluto."""
    cjf = load_youth_canteras_matriz_mart().copy()
    cjf["pct_juvenil"] = (100.0 - cjf["Absoluta"]).round(1)

    top_cantera_pct = (
        cjf[cjf["total"] >= 1000]
        .sort_values("pct_juvenil", ascending=False)
        .head(10)
        .sort_values("pct_juvenil", ascending=True)
    )

    top_cantera_vol = (
        cjf.sort_values("juveniles", ascending=False)
        .head(10)[["country", "juveniles"]]
        .sort_values("juveniles", ascending=True)
    )

    return top_cantera_pct, top_cantera_vol
