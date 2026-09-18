"""
Página 5 — Venezuela
======================
Descubrimiento: Radiografía del ajedrez venezolano en el contexto nacional e internacional.
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from components.charts import (
    fig_venezuela_hist,
    fig_venezuela_modalities,
    fig_venezuela_titles,
    fig_venezuela_youth,
)
from components.theme import render_page_header
from service.venezuela_service import (
    get_top_venezuelan_players,
    get_venezuela_elo_comparison,
    get_venezuela_kpis,
    get_venezuela_titles_summary,
    get_venezuela_youth_breakdown,
)

# ── Encabezado ─────────────────────────────────────────────────────────────────
render_page_header(
    "Venezuela",
    "Radiografía del ajedrez venezolano en el contexto nacional e internacional",
)

st.markdown(
    "El dataset de jugadores de **Venezuela** registrado ante la FIDE (~3.055 jugadores) "
    "muestra un perfil deportivo particular: una altísima concentración en partidas "
    "rápidas y blitz, un núcleo consolidado de maestros internacionales y una cantera "
    "formativa en crecimiento."
)
st.divider()

# ── Sección 1 — KPIs de Venezuela ──────────────────────────────────────────────
st.markdown("### El ajedrez venezolano en cifras")
kpis = get_venezuela_kpis()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Jugadores registrados",
    f"{kpis['total_ven']:,}",
    f"{kpis['pct_f']:.1f} % mujeres",
    help="Total de jugadores venezolanos registrados en el padrón oficial FIDE.",
)
c2.metric(
    "Jugadores titulados",
    f"{kpis['n_titulados']:,}",
    f"{kpis['n_gm']} GM · {kpis['n_im']} IM · {kpis['n_fm']} FM",
    help="Jugadores con títulos oficiales FIDE (GM, IM, FM, CM y títulos femeninos).",
)
c3.metric(
    "Ritmo predominante",
    f"Rápido ({kpis['n_rapid']:,})",
    f"{kpis['n_rapid'] / kpis['total_ven'] * 100:.1f} % del padrón",
    help="El ritmo Rápido supera con creces al Clásico en volumen de jugadores activos en Venezuela.",
)
c4.metric(
    "Cantera juvenil (Sub-20)",
    f"{kpis['n_youth']:,}",
    f"{kpis['pct_youth']:.1f} % del total",
    help="Jugadores venezolanos compitiendo en categorías Sub-8 a Sub-20.",
)

st.divider()

# ── Sección 2 — La paradoja del ritmo en Venezuela ─────────────────────────────
st.markdown("### La dinámica de ritmos: Rápido y Blitz frente al Clásico")

col_bar_ritmo, col_insight_ritmo = st.columns([3, 2])

with col_bar_ritmo:
    fig_modalities = fig_venezuela_modalities(
        kpis["n_classic"], kpis["n_rapid"], kpis["n_blitz"], kpis["total_ven"]
    )
    st.plotly_chart(fig_modalities, key="bar_ven_modalities")

with col_insight_ritmo:
    st.markdown("#### Hallazgo clave")
    st.info(
        "En Venezuela, **más del 72 %** de los jugadores tiene Elo en **Rápido** (2.217) "
        "y **69 % en Blitz** (2.110), mientras que solo el **31 %** cuenta con Elo "
        "en **Clásico** (947).\n\n"
        "A nivel mundial la relación es inversa: el Clásico suele ser el padrón más numeroso. "
        "En el contexto venezolano, los torneos de ritmo rápido de un solo día resultan "
        "mucho más accesibles económicamente y logísticamente para organizadores y jugadores."
    )

st.divider()

# ── Sección 3 — Distribución de Elo en Venezuela ───────────────────────────────
st.markdown("### Distribución del rating en Venezuela")

col_dist, col_table_kpi = st.columns([3, 2])

r_classic, r_rapid, r_blitz, comp_data = get_venezuela_elo_comparison()

with col_dist:
    fig_hist_ven = fig_venezuela_hist(r_classic, r_rapid)
    st.plotly_chart(fig_hist_ven, key="hist_ven_ratings")

with col_table_kpi:
    st.markdown("#### Comparativa de medianas")
    st.caption("Venezuela vs Padrón mundial activo.")
    st.dataframe(comp_data, hide_index=True, key="table_comp_ven")
    st.caption(
        "En ritmo Rápido, los jugadores venezolanos presentan una mediana (+6 pts) "
        "alineada con el promedio internacional, reflejando su competitividad en este formato."
    )

st.divider()

# ── Sección 4 — Estructura de Títulos en Venezuela ────────────────────────────
st.markdown("### Estructura de títulos oficiales en Venezuela")

title_kpis, df_titles_bar = get_venezuela_titles_summary()

col_tkpi1, col_tkpi2, col_tkpi3 = st.columns(3)
col_tkpi1.metric(
    "Sin título internacional",
    f"{title_kpis['sin_titulo_pct']:.1f} %",
    f"{title_kpis['sin_titulo_n']:,} jugadores",
    help="Jugadores venezolanos con Elo FIDE sin título internacional.",
)
col_tkpi2.metric(
    "Jugadores titulados",
    f"{title_kpis['titulados_pct']:.1f} %",
    f"{title_kpis['titulados_n']:,} titulados oficiales",
    help="Total de jugadores venezolanos con títulos GM, IM, FM, CM, WIM, WFM o WCM.",
)
col_tkpi3.metric(
    "Gran Maestro (GM)",
    f"{title_kpis['gm_n']}",
    "José Rafael Gascón Del Nogal",
    help="Máximo galardón del ajedrez mundial alcanzado en Venezuela.",
)

st.markdown("---")

col_tbars, col_tinsight = st.columns([3, 1])

with col_tbars:
    fig_ven_titles = fig_venezuela_titles(df_titles_bar)
    st.plotly_chart(fig_ven_titles, key="bars_ven_titles")

with col_tinsight:
    st.markdown("#### Hallazgo")
    st.info(
        "Venezuela cuenta con **85 maestros titulados**:\n\n"
        "- **1 GM** absoluto\n"
        "- **20 Maestros Internacionales** (16 IM + 4 WIM)\n"
        "- **27 Maestros FIDE** (22 FM + 5 WFM)\n"
        "- **37 Candidatos a Maestro** (33 CM + 4 WCM)\n\n"
        "La proporción de titulados (**2.8 %**) está prácticamente a la par del promedio mundial (3.2 %)."
    )

st.divider()

# ── Sección 5 — Top Jugadores Venezolanos ─────────────────────────────────────
st.markdown("### Cuadro de honor: Top jugadores de Venezuela")

col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
with col_filter1:
    modality_choice = st.selectbox("Ordenar por ritmo:", ["Clásico", "Rápido", "Blitz"], key="ven_sort_mode")
with col_filter2:
    category_filter = st.selectbox(
        "Filtrar por categoría:",
        ["Todas", "Solo Juveniles (Sub-8 a Sub-20)", "Sub 8", "Sub 10", "Sub 12", "Sub 14", "Sub 16", "Sub 18", "Sub 20", "Absoluta"],
        key="ven_cat_filter",
    )
with col_filter3:
    sex_filter = st.selectbox("Filtrar por género:", ["Todos", "Masculino", "Femenino"], key="ven_sex_filter")
with col_filter4:
    title_filter = st.selectbox("Filtrar por estatus:", ["Todos", "Solo titulados", "Sin título"], key="ven_title_filter")

display_table = get_top_venezuelan_players(modality_choice, category_filter, sex_filter, title_filter)
st.dataframe(display_table, hide_index=True, key="top_players_ven")
st.caption(f"Mostrando los mejores {len(display_table)} jugadores según los filtros seleccionados.")

st.divider()

# ── Sección 6 — Cantera venezolana ────────────────────────────────────────────
st.markdown("### La cantera venezolana por categorías")

ven_cats = get_venezuela_youth_breakdown()
fig_ven_cats = fig_venezuela_youth(ven_cats)
st.plotly_chart(fig_ven_cats, key="bar_ven_cats")
st.caption(
    "En Venezuela, las categorías **Sub-14, Sub-16 y Sub-18** agrupan al 67 % de todos los "
    "jugadores juveniles registrados, mostrando una sólida base en edades de secundaria y bachillerato."
)
