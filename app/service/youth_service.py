"""
app/service/youth_service.py
=============================
Servicio de datos analíticos para la página 04 — Cohortes Juveniles.
"""

from typing import Any, Dict, Tuple
import numpy as np
import pandas as pd

from components.theme import YOUTH_CATS
from service.data_loader import load_active_players, load_youth_categories


def get_youth_kpis() -> Dict[str, Any]:
    """Calcula las métricas principales del ajedrez juvenil mundial."""
    df_active = load_active_players()
    df_youth = df_active[df_active["categoria"].isin(YOUTH_CATS)].copy()

    total_active = len(df_active)
    total_youth = len(df_youth)
    pct_youth_global = total_youth / total_active * 100

    cat_summary = (
        df_youth.groupby(["categoria", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(YOUTH_CATS)
        .reset_index()
    )
    cat_summary.columns.name = None
    cat_summary["total"] = cat_summary["M"] + cat_summary["F"]

    peak_cat = cat_summary.loc[cat_summary["total"].idxmax(), "categoria"]
    peak_count = int(cat_summary["total"].max())

    # Curva para cambio de Elo Sub 8 -> Sub 20
    sub8 = df_youth[df_youth["categoria"] == "Sub 8"]["rating"]
    sub20 = df_youth[df_youth["categoria"] == "Sub 20"]["rating"]
    sub8_med = sub8[sub8 > 0].median() if len(sub8[sub8 > 0]) > 0 else 0
    sub20_med = sub20[sub20 > 0].median() if len(sub20[sub20 > 0]) > 0 else 0
    elo_diff = int(sub20_med - sub8_med)

    return {
        "total_youth": total_youth,
        "pct_youth_global": pct_youth_global,
        "peak_cat": peak_cat,
        "peak_count": peak_count,
        "elo_diff": elo_diff,
    }


def get_youth_categories_breakdown() -> pd.DataFrame:
    """Retorna el desglose por categoría juvenil y sexo."""
    df_active = load_active_players()
    df_youth = df_active[df_active["categoria"].isin(YOUTH_CATS)]

    cat_summary = (
        df_youth.groupby(["categoria", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(YOUTH_CATS)
        .reset_index()
    )
    cat_summary.columns.name = None
    cat_summary["total"] = cat_summary["M"] + cat_summary["F"]
    cat_summary["pct_F"] = (cat_summary["F"] / cat_summary["total"] * 100).round(1)
    return cat_summary


def get_youth_elo_curves_data() -> pd.DataFrame:
    """Calcula las curvas de desarrollo de medianas y percentiles de Elo por cohorte."""
    df_active = load_active_players()
    df_youth = df_active[df_active["categoria"].isin(YOUTH_CATS)]

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

    return pd.DataFrame(elo_curves)


def get_youth_canteras_summary() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula el Top de canteras por cuota % y por volumen absoluto."""
    cjf = load_youth_categories()
    df_active = load_active_players()
    df_youth = df_active[df_active["categoria"].isin(YOUTH_CATS)]

    cjf_copy = cjf.copy()
    cjf_copy["pct_juvenil"] = (100.0 - cjf_copy["Absoluta"]).round(1)

    top_cantera_pct = (
        cjf_copy[cjf_copy["total"] >= 1000]
        .sort_values("pct_juvenil", ascending=False)
        .head(10)
        .sort_values("pct_juvenil", ascending=True)
    )

    top_cantera_vol = (
        df_youth["country"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_cantera_vol.columns = ["country", "juveniles"]
    top_cantera_vol = top_cantera_vol.sort_values("juveniles", ascending=True)

    return top_cantera_pct, top_cantera_vol
