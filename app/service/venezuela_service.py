"""
app/service/venezuela_service.py
================================
Servicio de datos analíticos para la página 05 — Venezuela.
Consume los Data Marts precalculados (Capa Oro) y utiliza medianas mundiales dinámicas.
"""

from typing import Any, Dict, Tuple
import pandas as pd

from components.theme import CAT_ORDER, YOUTH_CATS
from service.data_loader import (
    load_venezuela_players,
    load_venezuela_comparativa_mart,
)

TITLES_ELITE = ["GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM"]


def get_venezuela_kpis() -> Dict[str, Any]:
    """Calcula los KPIs principales del ajedrez en Venezuela."""
    df_ven = load_venezuela_players()
    total_ven = len(df_ven)
    n_f = int((df_ven["sex"] == "F").sum())
    pct_f = n_f / total_ven * 100

    n_classic = int((df_ven["rating"] > 0).sum())
    n_rapid = int((df_ven["rapid_rating"] > 0).sum())
    n_blitz = int((df_ven["blitz_rating"] > 0).sum())

    df_titulados = df_ven[df_ven["title"].isin(TITLES_ELITE) | df_ven["w_title"].isin(TITLES_ELITE)]
    n_titulados = len(df_titulados)
    n_gm = int((df_ven["title"] == "GM").sum())
    n_im = int((df_ven["title"] == "IM").sum())
    n_fm = int((df_ven["title"] == "FM").sum())

    df_youth_ven = df_ven[df_ven["categoria"].isin(YOUTH_CATS)]
    n_youth = len(df_youth_ven)
    pct_youth = n_youth / total_ven * 100

    return {
        "total_ven": total_ven,
        "n_f": n_f,
        "pct_f": pct_f,
        "n_classic": n_classic,
        "n_rapid": n_rapid,
        "n_blitz": n_blitz,
        "n_titulados": n_titulados,
        "n_gm": n_gm,
        "n_im": n_im,
        "n_fm": n_fm,
        "n_youth": n_youth,
        "pct_youth": pct_youth,
    }


def get_venezuela_elo_comparison() -> Tuple[pd.Series, pd.Series, pd.Series, pd.DataFrame]:
    """Calcula las medianas comparativas de Venezuela vs el Mundo (dinámicas desde Capa Oro)."""
    df_ven = load_venezuela_players()
    r_classic = df_ven[df_ven["rating"] > 0]["rating"].dropna().astype(float)
    r_rapid = df_ven[df_ven["rapid_rating"] > 0]["rapid_rating"].dropna().astype(float)
    r_blitz = df_ven[df_ven["blitz_rating"] > 0]["blitz_rating"].dropna().astype(float)

    med_classic = int(r_classic.median()) if len(r_classic) > 0 else 0
    med_rapid = int(r_rapid.median()) if len(r_rapid) > 0 else 0
    med_blitz = int(r_blitz.median()) if len(r_blitz) > 0 else 0

    df_comp_world = load_venezuela_comparativa_mart()
    row_world = df_comp_world.iloc[0]
    world_classic = int(row_world["mediana_clasico_mundial"])
    world_rapid = int(row_world["mediana_rapido_mundial"])
    world_blitz = int(row_world["mediana_blitz_mundial"])

    comp_data = pd.DataFrame([
        {
            "Ritmo": "Clásico",
            "Mediana VEN": f"{med_classic:,}",
            "Mediana Mundial": f"{world_classic:,}",
            "Diferencia": f"{med_classic - world_classic:+d} pts",
        },
        {
            "Ritmo": "Rápido",
            "Mediana VEN": f"{med_rapid:,}",
            "Mediana Mundial": f"{world_rapid:,}",
            "Diferencia": f"{med_rapid - world_rapid:+d} pts",
        },
        {
            "Ritmo": "Blitz",
            "Mediana VEN": f"{med_blitz:,}",
            "Mediana Mundial": f"{world_blitz:,}",
            "Diferencia": f"{med_blitz - world_blitz:+d} pts",
        },
    ])

    return r_classic, r_rapid, r_blitz, comp_data


def get_venezuela_titles_summary() -> Tuple[Dict[str, Any], pd.DataFrame]:
    """Procesa el resumen y gráfico de barras de títulos oficiales en Venezuela."""
    df_ven = load_venezuela_players().copy()
    total_ven = len(df_ven)

    def _get_best_title(row):
        t = str(row["title"])
        wt = str(row["w_title"])
        if t != "nt":
            return t
        if wt != "nt":
            return wt
        return "nt"

    df_ven["best_title"] = df_ven.apply(_get_best_title, axis=1)
    ven_titles_counts = df_ven["best_title"].value_counts()

    sin_titulo_ven = int(ven_titles_counts.get("nt", 0))
    titulados_ven = total_ven - sin_titulo_ven

    title_names = {
        "GM": "Gran Maestro (GM)",
        "IM": "Maestro Internacional (IM)",
        "FM": "Maestro FIDE (FM)",
        "CM": "Candidato a Maestro (CM)",
        "WIM": "Maestra Internacional Fem. (WIM)",
        "WFM": "Maestra FIDE Fem. (WFM)",
        "WCM": "Candidata a Maestra (WCM)",
    }

    df_titles_bar = (
        pd.DataFrame([
            {"code": code, "label": title_names[code], "n": int(ven_titles_counts.get(code, 0))}
            for code in ["GM", "WCM", "WIM", "WFM", "IM", "FM", "CM"]
            if int(ven_titles_counts.get(code, 0)) > 0
        ])
        .sort_values("n", ascending=True)
    )

    kpis = {
        "total_ven": total_ven,
        "sin_titulo_n": sin_titulo_ven,
        "sin_titulo_pct": sin_titulo_ven / total_ven * 100,
        "titulados_n": titulados_ven,
        "titulados_pct": titulados_ven / total_ven * 100,
        "gm_n": int((df_ven["title"] == "GM").sum()),
    }


    return kpis, df_titles_bar


def get_top_venezuelan_players(
    modality_choice: str,
    category_filter: str,
    sex_filter: str,
    title_filter: str,
) -> pd.DataFrame:
    """Filtra y formatea la tabla del Top 20 jugadores venezolanos."""
    df_table = load_venezuela_players().copy()

    if category_filter == "Solo Juveniles (Sub-8 a Sub-20)":
        df_table = df_table[df_table["categoria"] != "Absoluta"]
    elif category_filter != "Todas":
        df_table = df_table[df_table["categoria"] == category_filter]

    if sex_filter == "Masculino":
        df_table = df_table[df_table["sex"] == "M"]
    elif sex_filter == "Femenino":
        df_table = df_table[df_table["sex"] == "F"]

    if title_filter == "Solo titulados":
        df_table = df_table[df_table["title"].isin(TITLES_ELITE) | df_table["w_title"].isin(TITLES_ELITE)]
    elif title_filter == "Sin título":
        df_table = df_table[(df_table["title"] == "nt") & (df_table["w_title"] == "nt")]

    sort_col = "rating" if modality_choice == "Clásico" else "rapid_rating" if modality_choice == "Rápido" else "blitz_rating"
    df_table = df_table[df_table[sort_col] > 0].sort_values(sort_col, ascending=False).head(20)

    display_table = pd.DataFrame({
        "#": range(1, len(df_table) + 1),
        "FIDE ID": df_table["fideid"].astype(str).values,
        "Nombre": df_table["name"].values,
        "Título": df_table["title"].astype(str).replace("nt", "—").values,
        "Título Fem.": df_table["w_title"].astype(str).replace("nt", "—").values,
        "Elo Clásico": df_table["rating"].apply(lambda v: f"{v:,}" if pd.notna(v) and v > 0 else "—").values,
        "Elo Rápido": df_table["rapid_rating"].apply(lambda v: f"{v:,}" if pd.notna(v) and v > 0 else "—").values,
        "Elo Blitz": df_table["blitz_rating"].apply(lambda v: f"{v:,}" if pd.notna(v) and v > 0 else "—").values,
        "Edad": df_table["edad"].values,
        "Categoría": df_table["categoria"].astype(str).values,
    })

    return display_table


def get_venezuela_youth_breakdown() -> pd.DataFrame:
    """Devuelve la distribución por categoría formativa en Venezuela."""
    df_ven = load_venezuela_players()
    ven_cats = (
        df_ven.groupby(["categoria", "sex"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(CAT_ORDER)
        .reset_index()
    )
    ven_cats.columns.name = None
    if "M" not in ven_cats.columns:
        ven_cats["M"] = 0
    if "F" not in ven_cats.columns:
        ven_cats["F"] = 0
    ven_cats["total"] = ven_cats["M"] + ven_cats["F"]
    return ven_cats
