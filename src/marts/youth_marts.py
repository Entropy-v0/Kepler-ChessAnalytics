"""
src/marts/youth_marts.py
=========================
Generador de Data Marts para Cohortes Juveniles (Página 04).
Precalcula curvas biológicas de desarrollo Elo, desglose formativo y canteras mundiales.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from loguru import logger

from src.config.constants import YOUTH_CATS


def build_youth_marts(df_active: pd.DataFrame, output_dir: Path) -> None:
    """Genera los Data Marts para el ajedrez juvenil y formativo."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generando Data Marts: Cohortes Juveniles...")

    df_youth = df_active[df_active["categoria"].isin(YOUTH_CATS)].copy()
    total_active = len(df_active)
    total_youth = len(df_youth)
    pct_youth_global = total_youth / total_active * 100

    # 1. Desglose de Categorías Juveniles
    cat_summary = (
        df_youth.groupby(["categoria", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(YOUTH_CATS)
        .reset_index()
    )
    cat_summary.columns.name = None
    if "M" not in cat_summary.columns:
        cat_summary["M"] = 0
    if "F" not in cat_summary.columns:
        cat_summary["F"] = 0
    cat_summary["total"] = cat_summary["M"] + cat_summary["F"]
    cat_summary["pct_F"] = (cat_summary["F"] / cat_summary["total"] * 100).round(1)

    cat_path = output_dir / "mart_youth_categorias.parquet"
    cat_summary.to_parquet(cat_path, index=False)
    logger.success(f"Guardado {cat_path.name}")

    # 2. KPIs Juveniles
    peak_cat = cat_summary.loc[cat_summary["total"].idxmax(), "categoria"]
    peak_count = int(cat_summary["total"].max())

    sub8 = df_youth[df_youth["categoria"] == "Sub 8"]["rating"]
    sub20 = df_youth[df_youth["categoria"] == "Sub 20"]["rating"]
    sub8_med = sub8[sub8 > 0].median() if len(sub8[sub8 > 0]) > 0 else 0
    sub20_med = sub20[sub20 > 0].median() if len(sub20[sub20 > 0]) > 0 else 0
    elo_diff = int(sub20_med - sub8_med)

    kpis_df = pd.DataFrame([{
        "total_youth": total_youth,
        "pct_youth_global": pct_youth_global,
        "peak_cat": peak_cat,
        "peak_count": peak_count,
        "elo_diff": elo_diff,
    }])
    kpis_path = output_dir / "mart_youth_kpis.parquet"
    kpis_df.to_parquet(kpis_path, index=False)
    logger.success(f"Guardado {kpis_path.name}")

    # 3. Curvas de Desarrollo de Elo por Cohorte
    elo_curves = []
    for cat in YOUTH_CATS:
        sub = df_youth[df_youth["categoria"] == cat]
        rc = sub[sub["rating"] > 0]["rating"].dropna().astype(float)
        rr = sub[sub["rapid_rating"] > 0]["rapid_rating"].dropna().astype(float)
        rb = sub[sub["blitz_rating"] > 0]["blitz_rating"].dropna().astype(float)

        elo_curves.append({
            "categoria": cat,
            "classic_med": rc.median() if len(rc) > 0 else np.nan,
            "classic_p25": rc.quantile(0.25) if len(rc) > 0 else np.nan,
            "classic_p75": rc.quantile(0.75) if len(rc) > 0 else np.nan,
            "classic_p90": rc.quantile(0.90) if len(rc) > 0 else np.nan,
            "classic_p99": rc.quantile(0.99) if len(rc) > 0 else np.nan,
            "rapid_med": rr.median() if len(rr) > 0 else np.nan,
            "blitz_med": rb.median() if len(rb) > 0 else np.nan,
            "n_classic": len(rc),
        })

    curves_df = pd.DataFrame(elo_curves)
    curves_path = output_dir / "mart_youth_elo_curves.parquet"
    curves_df.to_parquet(curves_path, index=False)
    logger.success(f"Guardado {curves_path.name}")

    # 4. Canteras Mundiales (Porcentaje y Volumen)
    # Genera la matriz porcentual de categorías por federación (corrige cateogrias_juveniles_fed)
    ctab = (
        df_active.groupby(["country", "categoria"], observed=True)
        .size()
        .unstack(fill_value=0)
    )
    total_per_country = ctab.sum(axis=1)
    juveniles_per_country = ctab[[c for c in YOUTH_CATS if c in ctab.columns]].sum(axis=1)

    ctab_pct = (ctab.div(total_per_country, axis=0) * 100).round(2)
    ctab_pct.insert(0, "juveniles", juveniles_per_country)
    ctab_pct.insert(0, "total", total_per_country)
    ctab_pct = ctab_pct.reset_index()

    canteras_path = output_dir / "mart_youth_canteras_matriz.parquet"
    ctab_pct.to_parquet(canteras_path, index=False)
    logger.success(f"Guardado {canteras_path.name}")

