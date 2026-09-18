"""
src/marts/venezuela_marts.py
=============================
Generador de Data Marts para Venezuela (Página 05).
Filtra el padrón nacional y calcula métricas robustas de posición relativa (percentiles locales y Z-scores por IQR).
"""

from pathlib import Path
from typing import Tuple
import pandas as pd
from loguru import logger


def build_venezuela_marts(df_active: pd.DataFrame, output_dir: Path) -> None:
    """
    Genera mart_venezuela.parquet y mart_venezuela_comparativa.parquet.
    Aplica cálculo estadístico robusto de percentiles y Z-Score basado en IQR por categoría.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generando Data Marts: Venezuela...")

    # Copia de trabajo para cálculo estadístico
    df_calc = df_active.copy()
    columnas_elo = ["rating", "rapid_rating", "blitz_rating"]

    for col in columnas_elo:
        # Percentil relativo dentro de la categoría y país
        df_calc[f"percentil_{col}_local"] = df_calc.groupby(
            ["categoria", "country"], observed=True
        )[col].rank(pct=True)

        # Parámetros robustos locales (mediana e IQR)
        mediana_local = df_calc.groupby(["categoria", "country"], observed=True)[col].transform("median")
        q1_local = df_calc.groupby(["categoria", "country"], observed=True)[col].transform(lambda x: x.quantile(0.25))
        q3_local = df_calc.groupby(["categoria", "country"], observed=True)[col].transform(lambda x: x.quantile(0.75))
        iqr_local = q3_local - q1_local

        # Parámetros robustos globales de respaldo
        mediana_global = df_calc.groupby("categoria", observed=True)[col].transform("median")
        q1_global = df_calc.groupby("categoria", observed=True)[col].transform(lambda x: x.quantile(0.25))
        q3_global = df_calc.groupby("categoria", observed=True)[col].transform(lambda x: x.quantile(0.75))
        iqr_global = q3_global - q1_global

        n_local = df_calc.groupby(["categoria", "country"], observed=True)[col].transform("count")

        # Regla de respaldo si la muestra local es muy pequeña o IQR es cero
        condicion = (iqr_local == 0) | (n_local < 5)
        iqr_efectivo = iqr_local.mask(condicion, iqr_global)
        mediana_efectiva = mediana_local.mask(condicion, mediana_global)

        iqr_efectivo = pd.to_numeric(iqr_efectivo, errors="coerce")
        mediana_efectiva = pd.to_numeric(mediana_efectiva, errors="coerce")

        # Z-score robusto basado en IQR
        calculo_z_score = (df_calc[col] - mediana_efectiva) / (iqr_efectivo + 1e-5)
        df_calc[f"z_score_{col}_local"] = pd.to_numeric(calculo_z_score, errors="coerce")

    # Filtrar solo jugadores de Venezuela
    df_ven = df_calc[df_calc["country"] == "VEN"].copy().reset_index(drop=True)

    ven_path = output_dir / "mart_venezuela.parquet"
    df_ven.to_parquet(ven_path, index=False)
    logger.success(f"Guardado {ven_path.name} ({len(df_ven):,} registros, {ven_path.stat().st_size:,} bytes)")

    # 2. Mart de Medianas Mundiales Dinámicas (reemplaza los valores hardcodeados '1 707', etc.)
    r_classic_world = df_active[df_active["rating"] > 0]["rating"].dropna().astype(float)
    r_rapid_world = df_active[df_active["rapid_rating"] > 0]["rapid_rating"].dropna().astype(float)
    r_blitz_world = df_active[df_active["blitz_rating"] > 0]["blitz_rating"].dropna().astype(float)

    comp_world_df = pd.DataFrame([{
        "mediana_clasico_mundial": int(r_classic_world.median()) if len(r_classic_world) > 0 else 1707,
        "mediana_rapido_mundial": int(r_rapid_world.median()) if len(r_rapid_world) > 0 else 1635,
        "mediana_blitz_mundial": int(r_blitz_world.median()) if len(r_blitz_world) > 0 else 1688,
    }])

    comp_path = output_dir / "mart_venezuela_comparativa.parquet"
    comp_world_df.to_parquet(comp_path, index=False)
    logger.success(f"Guardado {comp_path.name}")
