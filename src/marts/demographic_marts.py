"""
src/marts/demographic_marts.py
===============================
Generador de Data Marts para Demografía y Género (Página 03).
Precalcula pirámide etaria, ratios de género por federación y estructura por categorías.
"""

from pathlib import Path
import pandas as pd
from loguru import logger

from src.config.constants import CAT_ORDER


def build_demographic_marts(df_active: pd.DataFrame, output_dir: Path) -> None:
    """Genera los Data Marts para demografía y análisis de género."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generando Data Marts: Demografía y Género...")

    total = len(df_active)
    n_m = int((df_active["sex"] == "M").sum())
    n_f = int((df_active["sex"] == "F").sum())
    pct_m = n_m / total * 100
    pct_f = n_f / total * 100

    df_youth = df_active[df_active["categoria"] != "Absoluta"]
    n_youth = len(df_youth)
    pct_youth = n_youth / total * 100
    pct_f_youth = (df_youth["sex"] == "F").mean() * 100

    df_adult = df_active[df_active["categoria"] == "Absoluta"]
    pct_f_adult = (df_adult["sex"] == "F").mean() * 100

    # 1. KPIs Demográficos
    kpis_df = pd.DataFrame([{
        "n_m": n_m,
        "n_f": n_f,
        "pct_m": pct_m,
        "pct_f": pct_f,
        "n_youth": n_youth,
        "pct_youth": pct_youth,
        "pct_f_youth": pct_f_youth,
        "pct_f_adult": pct_f_adult,
        "drop_pp": pct_f_youth - pct_f_adult,
    }])
    kpis_path = output_dir / "mart_demografia_kpis.parquet"
    kpis_df.to_parquet(kpis_path, index=False)
    logger.success(f"Guardado {kpis_path.name}")

    # 2. Ratio de Género por Federaciones (Top 50)
    top_feds = df_active["country"].value_counts().head(50).index.tolist()
    fed_sex = (
        df_active[df_active["country"].isin(top_feds)]
        .groupby(["country", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    fed_sex.columns.name = None
    if "M" not in fed_sex.columns:
        fed_sex["M"] = 0
    if "F" not in fed_sex.columns:
        fed_sex["F"] = 0
    fed_sex["total"] = fed_sex["M"] + fed_sex["F"]
    fed_sex["pct_F"] = (fed_sex["F"] / fed_sex["total"] * 100).round(1)
    fed_sex["pct_M"] = (fed_sex["M"] / fed_sex["total"] * 100).round(1)
    fed_sex = fed_sex.sort_values("total", ascending=True)

    fed_path = output_dir / "mart_demografia_federaciones.parquet"
    fed_sex.to_parquet(fed_path, index=False)
    logger.success(f"Guardado {fed_path.name}")

    # 3. Estructura por Categorías FIDE
    cat_df = (
        df_active.groupby(["categoria", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(CAT_ORDER)
        .reset_index()
    )
    cat_df.columns.name = None
    if "M" not in cat_df.columns:
        cat_df["M"] = 0
    if "F" not in cat_df.columns:
        cat_df["F"] = 0
    cat_df["total"] = cat_df["M"] + cat_df["F"]
    cat_df["pct_F"] = (cat_df["F"] / cat_df["total"] * 100).round(1)
    cat_df["pct_M"] = (cat_df["M"] / cat_df["total"] * 100).round(1)

    cat_path = output_dir / "mart_demografia_categorias.parquet"
    cat_df.to_parquet(cat_path, index=False)
    logger.success(f"Guardado {cat_path.name}")

    # 4. Pirámide Quinquenal de Edad
    age_bins = list(range(0, 100, 5)) + [100]
    age_labels = [f"{i}–{i+4}" for i in range(0, 95, 5)] + ["95+"]

    df_copy = df_active[["edad", "sex"]].copy()
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

    pyramid_path = output_dir / "mart_demografia_piramide.parquet"
    pyramid_age.to_parquet(pyramid_path, index=False)
    logger.success(f"Guardado {pyramid_path.name}")

    # 5. Paridad por País (Mínimo 500 jugadores)
    fed_all = (
        df_active.groupby(["country", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    fed_all.columns.name = None
    if "M" not in fed_all.columns:
        fed_all["M"] = 0
    if "F" not in fed_all.columns:
        fed_all["F"] = 0
    fed_all["total"] = fed_all["M"] + fed_all["F"]
    fed_all["pct_F"] = (fed_all["F"] / fed_all["total"] * 100).round(1)
    parity_df = fed_all[fed_all["total"] >= 500].sort_values("pct_F", ascending=False)

    parity_path = output_dir / "mart_demografia_paridad.parquet"
    parity_df.to_parquet(parity_path, index=False)
    logger.success(f"Guardado {parity_path.name}")
