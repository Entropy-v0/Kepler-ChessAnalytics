"""
app/service/elo_service.py
===========================
Servicio de datos analíticos para la página 02 — Distribución de Elo.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from service.data_loader import load_all_players

SAMPLE_N = 60_000


def get_elo_kpis() -> Dict[str, int]:
    """Calcula los percentiles y la media del rating Clásico."""
    df = load_all_players()
    classic = df[df["rating"] > 0]["rating"].dropna().astype(float)
    return {
        "p25": int(classic.quantile(0.25)),
        "p50": int(classic.quantile(0.50)),
        "p75": int(classic.quantile(0.75)),
        "p99": int(classic.quantile(0.99)),
        "mean": int(classic.mean()),
        "p10": int(classic.quantile(0.10)),
        "p90": int(classic.quantile(0.90)),
        "total_classic": len(classic),
    }


def get_kde_data(
    show_classic: bool = True,
    show_rapid: bool = True,
    show_blitz: bool = True,
) -> Tuple[List[Tuple[str, np.ndarray, np.ndarray]], int, float]:
    """Calcula las curvas KDE para las modalidades seleccionadas."""
    df = load_all_players()

    def _sample(series: pd.Series, n: int) -> np.ndarray:
        s = series[series > 0].dropna().astype(float)
        return s.sample(min(n, len(s)), random_state=42).values

    x_grid = np.linspace(1380, 2860, 600)
    results = []

    if show_classic:
        data = _sample(df["rating"], SAMPLE_N)
        kde = gaussian_kde(data, bw_method=0.08)
        results.append(("Clásico", x_grid, kde(x_grid)))
    if show_rapid:
        data = _sample(df["rapid_rating"], SAMPLE_N)
        kde = gaussian_kde(data, bw_method=0.08)
        results.append(("Rápido", x_grid, kde(x_grid)))
    if show_blitz:
        data = _sample(df["blitz_rating"], SAMPLE_N)
        kde = gaussian_kde(data, bw_method=0.08)
        results.append(("Blitz", x_grid, kde(x_grid)))

    classic_full = df[df["rating"] > 0]["rating"].dropna().astype(float)
    p50_classic = int(classic_full.quantile(0.50))
    kde_classic_full = gaussian_kde(_sample(df["rating"], SAMPLE_N), bw_method=0.08)
    y_p50 = float(kde_classic_full(p50_classic)[0])

    return results, p50_classic, y_p50


def get_classic_ratings_series() -> pd.Series:
    """Devuelve la serie de ratings clásicos válidos para histograma."""
    df = load_all_players()
    return df[df["rating"] > 0]["rating"].dropna().astype(float)


def get_title_structure_summary() -> Tuple[Dict[str, Any], pd.DataFrame]:
    """Procesa el resumen de títulos mundiales y el desglose de titulados."""
    df = load_all_players()
    total = len(df)

    title_map = {
        "GM": "Gran Maestro",
        "IM": "Maestro Internacional",
        "FM": "Maestro FIDE",
        "CM": "Candidato a Maestro",
        "WGM": "WGM",
        "WIM": "WIM",
        "WFM": "WFM",
        "WCM": "WCM",
        "nt": "Sin título",
    }
    title_counts = df["title"].value_counts().reset_index()
    title_counts.columns = ["title", "n"]
    title_counts["label"] = title_counts["title"].map(title_map).fillna(title_counts["title"])

    sin_titulo_n = int(title_counts.loc[title_counts["title"] == "nt", "n"].values[0])
    sin_titulo_pct = sin_titulo_n / total * 100
    titulados_n = total - sin_titulo_n
    titulados_pct = titulados_n / total * 100
    gm_n = int(title_counts.loc[title_counts["title"] == "GM", "n"].values[0])
    fm_n = int(title_counts.loc[title_counts["title"] == "FM", "n"].values[0])
    im_n = int(title_counts.loc[title_counts["title"] == "IM", "n"].values[0])

    kpis = {
        "sin_titulo_n": sin_titulo_n,
        "sin_titulo_pct": sin_titulo_pct,
        "titulados_n": titulados_n,
        "titulados_pct": titulados_pct,
        "gm_n": gm_n,
        "fm_n": fm_n,
        "im_n": im_n,
    }

    titled_df = (
        title_counts[title_counts["title"] != "nt"]
        .copy()
        .sort_values("n", ascending=True)
    )

    return kpis, titled_df


def get_titles_heatmap_data(top_feds_n: int = 12) -> pd.DataFrame:
    """Construye la matriz de marcas GM, IM, FM para el Top N federaciones."""
    df = load_all_players()
    heatmap_titles = ["GM", "IM", "FM"]
    top_feds = (
        df[df["title"].isin(heatmap_titles)]["country"]
        .value_counts()
        .head(top_feds_n)
        .index.tolist()
    )

    heat_df = (
        df[df["title"].isin(heatmap_titles) & df["country"].isin(top_feds)]
        .groupby(["country", "title"], observed=True)
        .size()
        .reset_index(name="n")
        .pivot(index="country", columns="title", values="n")
        .fillna(0)
        .astype(int)
    )
    heat_df = heat_df.loc[heat_df.sum(axis=1).sort_values(ascending=False).index]
    return heat_df[heatmap_titles]
