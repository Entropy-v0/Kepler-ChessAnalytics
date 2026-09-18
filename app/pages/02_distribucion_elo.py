"""
Página 2 — Distribución de Elo
================================
Descubrimiento: ¿Cómo se mide y distribuye el nivel en el ajedrez mundial?
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from components.charts import (
    fig_bar_titles,
    fig_heatmap_titles,
    fig_hist_classic_percentiles,
    fig_kde_modalities,
)
from components.theme import render_page_header
from service.elo_service import (
    get_classic_histogram_data,
    get_elo_kpis,
    get_kde_data,
    get_title_structure_summary,
    get_titles_heatmap_data,
)


# ── Encabezado ─────────────────────────────────────────────────────────────────
render_page_header("Distribución de Elo", "¿Cómo se mide y distribuye el nivel en el ajedrez mundial?")

st.markdown(
    "El **sistema Elo** cuantifica la fuerza de un jugador en base a sus resultados "
    "contra otros. La FIDE publica ratings en tres modalidades: "
    "**Clásico** (partidas largas), **Rápido** y **Blitz** (relámpago)."
)
st.divider()

# ── Sección 1 — KPIs de rating ────────────────────────────────────────────────
st.markdown("### El rating en cifras")
kpis = get_elo_kpis()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Mediana Clásico", f"{kpis['p50']:,}", help="El 50 % de los jugadores está por debajo de este valor.")
c2.metric("Media Clásico", f"{kpis['mean']:,}", help="Promedio aritmético del rating clásico.")
c3.metric("P25", f"{kpis['p25']:,}", help="El 25 % de los jugadores tiene un rating inferior.")
c4.metric("P75", f"{kpis['p75']:,}", help="El 75 % de los jugadores tiene un rating inferior.")
c5.metric("P99 (élite)", f"{kpis['p99']:,}", help="Solo el 1 % supera este umbral.")

st.divider()

# ── Sección 2 — KDE Comparativo ───────────────────────────────────────────────
st.markdown("### Densidad de ratings: Clásico vs Rápido vs Blitz")

@st.fragment
def render_kde_modalities_section() -> None:
    col_kde, col_ins = st.columns([3, 1])

    with col_ins:
        st.markdown("#### Filtrar modalidades")
        show_classic = st.checkbox("Clásico", value=True)
        show_rapid = st.checkbox("Rápido", value=True)
        show_blitz = st.checkbox("Blitz", value=True)
        st.markdown("---")
        st.markdown("#### Hallazgo")
        st.info(
            "Las tres curvas **no coinciden**: el Rápido tiene la mediana más baja "
            "(~1 635), seguido del Blitz (~1 688) y el Clásico (~1 707).\n\n"
            "Esto refleja que muchos jugadores compiten en Rápido y Blitz sin haber "
            "acumulado suficientes partidas Clásico para que su rating madure."
        )

    with col_kde:
        kde_curves, p50_classic, y_p50 = get_kde_data(show_classic, show_rapid, show_blitz)
        fig_kde = fig_kde_modalities(kde_curves, p50_classic, y_p50)
        st.plotly_chart(fig_kde, key="kde_ratings")


render_kde_modalities_section()


st.divider()

# ── Sección 3 — Histograma + percentiles ──────────────────────────────────────
st.markdown("### Histograma del rating Clásico con percentiles")

hist_df, max_rating = get_classic_histogram_data()
percs = {
    "P10": (kpis["p10"], "#48CAE4"),
    "P25": (kpis["p25"], "#2ECC71"),
    "Mediana": (kpis["p50"], "#E84855"),
    "P75": (kpis["p75"], "#F39C12"),
    "P90": (kpis["p90"], "#8E44AD"),
    "P99": (kpis["p99"], "#1C2333"),
}

fig_hist = fig_hist_classic_percentiles(hist_df, percs)
st.plotly_chart(fig_hist, key="hist_classic")
st.caption(
    f"Basado en {kpis['total_classic']:,} jugadores con rating Clásico > 0. "
    f"Rango real: 1 400 – {max_rating:,}. "
    "Bins de 20 puntos. Las líneas de percentiles muestran P10, P25, P50, P75, P90 y P99."
)


st.divider()

# ── Sección 4 — KPI + barras de títulos ───────────────────────────────────────
st.markdown("### Estructura de títulos mundiales")
title_kpis, titled_df = get_title_structure_summary()

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric(
    "Sin título internacional",
    f"{title_kpis['sin_titulo_pct']:.1f} %",
    f"{title_kpis['sin_titulo_n']:,} jugadores",
    help="Jugadores registrados en la FIDE sin ningún título federativo.",
)
col_kpi2.metric(
    "Con algún título",
    f"{title_kpis['titulados_pct']:.1f} %",
    f"{title_kpis['titulados_n']:,} jugadores",
    help="Jugadores con al menos un título internacional (GM, IM, FM, CM, WGM, WIM, WFM, WCM).",
)
col_kpi3.metric(
    "Gran Maestro (GM)",
    f"{title_kpis['gm_n']:,}",
    "el título más alto",
    help="Solo 1 899 jugadores en el mundo han alcanzado el título de Gran Maestro.",
)

st.markdown("---")
st.markdown("#### Desglose de los jugadores titulados")
st.caption("Excluye 'Sin título' para que los valores pequeños sean visibles.")

col_bars, col_insight = st.columns([3, 1])

with col_bars:
    fig_bars = fig_bar_titles(titled_df)
    st.plotly_chart(fig_bars, key="bars_titles")

with col_insight:
    st.markdown("#### Hallazgo")
    st.info(
        "La pirámide de títulos es **extremadamente estrecha**:\n\n"
        f"- **FM** (Maestro FIDE): {title_kpis['fm_n']:,}\n"
        f"- **IM** (M. Internacional): {title_kpis['im_n']:,}\n"
        f"- **GM** (Gran Maestro): {title_kpis['gm_n']:,}\n\n"
        "Por cada GM hay **~5 IMs** y **~5 FMs**. "
        "Ascender de FM a GM es el salto más difícil del ajedrez competitivo."
    )

st.divider()

# ── Sección 5 — Heatmap de títulos por federación ─────────────────────────────
TOP_FEDS_N = 12
st.markdown("### Concentración de élite: GM · IM · FM por federación")
st.caption(f"Top {TOP_FEDS_N} federaciones por volumen total de jugadores titulados de élite.")

heat_df = get_titles_heatmap_data(top_feds_n=TOP_FEDS_N)
fig_heat = fig_heatmap_titles(heat_df)
st.plotly_chart(fig_heat, key="heatmap_titles")
st.caption(
    "Rusia domina en todas las categorías. Alemania ocupa el segundo lugar en IMs y FMs, "
    "mientras que India crece rápidamente en GMs gracias a su programa nacional de ajedrez."
)
