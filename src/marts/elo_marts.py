"""
src/marts/elo_marts.py
=======================
Generador de Data Marts para Distribución de Elo (Página 02).
Precalcula percentiles, densidades KDE con Scipy y desglose de títulos FIDE.
"""

from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from loguru import logger

from src.config.constants import TITLE_NAMES


SAMPLE_N = 60_000


def build_elo_marts(df_all: pd.DataFrame, output_dir: Path) -> None:
    """Genera Data Marts analíticos para ratings y títulos oficiales."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generando Data Marts: Distribución de Elo y Títulos...")

    classic = df_all[df_all["rating"] > 0]["rating"].dropna().astype(float)
    total = len(df_all)

    # 1. Mart de KPIs de Rating Clásico
    elo_kpis_df = pd.DataFrame([{
        "p10": int(classic.quantile(0.10)),
        "p25": int(classic.quantile(0.25)),
        "p50": int(classic.quantile(0.50)),
        "p75": int(classic.quantile(0.75)),
        "p90": int(classic.quantile(0.90)),
        "p99": int(classic.quantile(0.99)),
        "mean": int(classic.mean()),
        "total_classic": int(len(classic)),
    }])
    kpis_path = output_dir / "mart_elo_kpis.parquet"
    elo_kpis_df.to_parquet(kpis_path, index=False)
    logger.success(f"Guardado {kpis_path.name}")

    # 2. Mart de Curvas KDE Precalculadas (Elimina Scipy de Streamlit)
    def _sample(series: pd.Series, n: int) -> np.ndarray:
        s = series[series > 0].dropna().astype(float)
        return s.sample(min(n, len(s)), random_state=42).values

    x_grid = np.linspace(1380, 2860, 600)
    p50_classic = int(classic.quantile(0.50))
    kde_classic_full = gaussian_kde(_sample(df_all["rating"], SAMPLE_N), bw_method=0.08)
    y_p50 = float(kde_classic_full(p50_classic)[0])

    kde_records = []
    modalidades = [
        ("Clásico", df_all["rating"]),
        ("Rápido", df_all["rapid_rating"]),
        ("Blitz", df_all["blitz_rating"]),
    ]

    for name, series in modalidades:
        data = _sample(series, SAMPLE_N)
        kde = gaussian_kde(data, bw_method=0.08)
        densities = kde(x_grid)
        for x_val, d_val in zip(x_grid, densities):
            kde_records.append({
                "modalidad": name,
                "x": float(x_val),
                "density": float(d_val),
                "p50_classic": p50_classic,
                "y_p50_classic": y_p50,
            })

    kde_df = pd.DataFrame(kde_records)
    kde_path = output_dir / "mart_kde_ratings.parquet"
    kde_df.to_parquet(kde_path, index=False)
    logger.success(f"Guardado {kde_path.name} (KDE precalculado)")

    # 3. Mart de Histograma Precalculado (Pre-binning para go.Bar en Plotly, reduce JSON de 3 MB a 1.8 KB)
    bins = np.arange(1400, 2880 + 20, 20)
    counts, bin_edges = np.histogram(classic, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    hist_df = pd.DataFrame({
        "bin_start": bin_edges[:-1].astype(int),
        "bin_end": bin_edges[1:].astype(int),
        "bin_center": bin_centers.astype(float),
        "count": counts.astype(int),
        "max_rating": int(classic.max()) if len(classic) > 0 else 2880,
    })
    hist_path = output_dir / "mart_histograma_clasico.parquet"
    hist_df.to_parquet(hist_path, index=False)
    logger.success(f"Guardado {hist_path.name} (Histograma pre-binned: {len(hist_df)} bins)")

    # 4. Mart de Serie de Ratings Clásicos (respaldo/auditoría)
    classic_series_df = pd.DataFrame({"rating": classic.astype(np.int32)})
    series_path = output_dir / "mart_ratings_clasico.parquet"
    classic_series_df.to_parquet(series_path, index=False)
    logger.success(f"Guardado {series_path.name} ({series_path.stat().st_size:,} bytes)")


    # 4. Mart de Resumen de Títulos FIDE
    title_counts = df_all["title"].value_counts().reset_index()
    title_counts.columns = ["title", "n"]
    title_counts["label"] = title_counts["title"].map(TITLE_NAMES).fillna(title_counts["title"])

    sin_titulo_n = int(title_counts.loc[title_counts["title"] == "nt", "n"].values[0]) if (title_counts["title"] == "nt").any() else 0
    sin_titulo_pct = sin_titulo_n / total * 100
    titulados_n = total - sin_titulo_n
    titulados_pct = titulados_n / total * 100
    gm_n = int(title_counts.loc[title_counts["title"] == "GM", "n"].values[0]) if (title_counts["title"] == "GM").any() else 0
    fm_n = int(title_counts.loc[title_counts["title"] == "FM", "n"].values[0]) if (title_counts["title"] == "FM").any() else 0
    im_n = int(title_counts.loc[title_counts["title"] == "IM", "n"].values[0]) if (title_counts["title"] == "IM").any() else 0

    title_counts["sin_titulo_n"] = sin_titulo_n
    title_counts["sin_titulo_pct"] = sin_titulo_pct
    title_counts["titulados_n"] = titulados_n
    title_counts["titulados_pct"] = titulados_pct
    title_counts["gm_n"] = gm_n
    title_counts["fm_n"] = fm_n
    title_counts["im_n"] = im_n

    titulos_resumen_path = output_dir / "mart_titulos_resumen.parquet"
    title_counts.to_parquet(titulos_resumen_path, index=False)
    logger.success(f"Guardado {titulos_resumen_path.name}")

    # 5. Mart de Heatmap de Títulos por Federación
    heatmap_titles = ["GM", "IM", "FM"]
    top_feds = (
        df_all[df_all["title"].isin(heatmap_titles)]["country"]
        .value_counts()
        .head(30)
        .index.tolist()
    )

    heat_df = (
        df_all[df_all["title"].isin(heatmap_titles) & df_all["country"].isin(top_feds)]
        .groupby(["country", "title"], observed=True)
        .size()
        .reset_index(name="n")
        .pivot(index="country", columns="title", values="n")
        .fillna(0)
        .astype(int)
    )
    heat_df["total_elite"] = heat_df.sum(axis=1)
    heat_df = heat_df.sort_values("total_elite", ascending=False).reset_index()

    heatmap_path = output_dir / "mart_titulos_federacion.parquet"
    heat_df.to_parquet(heatmap_path, index=False)
    logger.success(f"Guardado {heatmap_path.name}")
