"""
app/service/elo_service.py
===========================
Servicio de datos analíticos para la página 02 — Distribución de Elo.
Consume los Data Marts precalculados (Capa Oro), eliminando cálculos de Scipy en runtime.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from service.data_loader import (
    load_elo_kpis_mart,
    load_kde_ratings_mart,
    load_ratings_clasico_mart,
    load_histograma_clasico_mart,
    load_titulos_resumen_mart,
    load_titulos_federacion_mart,
)



def get_elo_kpis() -> Dict[str, int]:
    """Calcula los percentiles y la media del rating Clásico."""
    df_kpis = load_elo_kpis_mart()
    row = df_kpis.iloc[0]
    return {
        "p25": int(row["p25"]),
        "p50": int(row["p50"]),
        "p75": int(row["p75"]),
        "p99": int(row["p99"]),
        "mean": int(row["mean"]),
        "p10": int(row["p10"]),
        "p90": int(row["p90"]),
        "total_classic": int(row["total_classic"]),
    }


def get_kde_data(
    show_classic: bool = True,
    show_rapid: bool = True,
    show_blitz: bool = True,
) -> Tuple[List[Tuple[str, np.ndarray, np.ndarray]], int, float]:
    """Retorna las curvas KDE precalculadas para las modalidades seleccionadas."""
    df_kde = load_kde_ratings_mart()
    p50_classic = int(df_kde["p50_classic"].iloc[0])
    y_p50 = float(df_kde["y_p50_classic"].iloc[0])

    results = []
    modalidades_activas = []
    if show_classic:
        modalidades_activas.append("Clásico")
    if show_rapid:
        modalidades_activas.append("Rápido")
    if show_blitz:
        modalidades_activas.append("Blitz")

    for name in modalidades_activas:
        sub = df_kde[df_kde["modalidad"] == name]
        results.append((name, sub["x"].values, sub["density"].values))

    return results, p50_classic, y_p50


def get_classic_ratings_series() -> pd.Series:
    """Devuelve la serie de ratings clásicos válidos para histograma (compatibilidad)."""
    df_classic = load_ratings_clasico_mart()
    return df_classic["rating"]


def get_classic_histogram_data() -> Tuple[pd.DataFrame, int]:
    """Devuelve los bins del histograma clásico precalculados y el rating máximo."""
    df_hist = load_histograma_clasico_mart()
    max_rating = int(df_hist["max_rating"].iloc[0]) if "max_rating" in df_hist.columns else 2880
    return df_hist, max_rating



def get_title_structure_summary() -> Tuple[Dict[str, Any], pd.DataFrame]:
    """Procesa el resumen de títulos mundiales y el desglose de titulados."""
    df_titles = load_titulos_resumen_mart()
    first = df_titles.iloc[0]

    kpis = {
        "sin_titulo_n": int(first["sin_titulo_n"]),
        "sin_titulo_pct": float(first["sin_titulo_pct"]),
        "titulados_n": int(first["titulados_n"]),
        "titulados_pct": float(first["titulados_pct"]),
        "gm_n": int(first["gm_n"]),
        "fm_n": int(first["fm_n"]),
        "im_n": int(first["im_n"]),
    }

    titled_df = (
        df_titles[df_titles["title"] != "nt"][["title", "n", "label"]]
        .copy()
        .sort_values("n", ascending=True)
    )

    return kpis, titled_df


def get_titles_heatmap_data(top_feds_n: int = 12) -> pd.DataFrame:
    """Construye la matriz de marcas GM, IM, FM para el Top N federaciones."""
    df_heat = load_titulos_federacion_mart()
    heatmap_titles = ["GM", "IM", "FM"]
    matrix = df_heat.head(top_feds_n).set_index("country")[heatmap_titles].copy()
    return matrix
