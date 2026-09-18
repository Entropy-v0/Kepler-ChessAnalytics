"""
Página 1 — Panorama Global
===========================
Descubrimiento: ¿Dónde se juega ajedrez en el mundo?
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from components.charts import fig_bar_top_federations, fig_map_world
from components.theme import render_page_header
from service.global_service import (
    get_global_kpis,
    get_top_federations_summary,
    get_world_map_data,
)

# ── Encabezado ─────────────────────────────────────────────────────────────────
render_page_header("Panorama Global", "¿Dónde se juega ajedrez en el mundo?")

st.markdown(
    "El padrón oficial de la **FIDE** registra a todos los jugadores que han "
    "competido en torneos federados a nivel internacional. Exploremos cómo se "
    "distribuyen geográficamente."
)
st.divider()

# ── Sección 1 — KPIs ──────────────────────────────────────────────────────────
st.markdown("### Cifras del padrón mundial")
kpis = get_global_kpis()

c1, c2, c3 = st.columns(3)
c1.metric(
    label="Jugadores registrados",
    value=f"{kpis['total_players']:,}".replace(",", "."),
    help="Jugadores con al menos un rating > 0 y año de nacimiento válido.",
)
c2.metric(
    label="Jugadores activos",
    value=f"{kpis['active_players']:,}".replace(",", "."),
    help="Jugadores sin flag de inactividad FIDE.",
)
c3.metric(
    label="Países / Federaciones",
    value=str(kpis["total_countries"]),
    help="Número de federaciones nacionales con al menos un jugador registrado.",
)

st.divider()

# ── Sección 2 — Barras horizontales ───────────────────────────────────────────
fed_counts, TOP_N = get_top_federations_summary(top_n=15)
st.markdown(f"### Top {TOP_N} federaciones por número de jugadores")

col_chart, col_insight = st.columns([3, 1])

with col_chart:
    st.plotly_chart(fig_bar_top_federations(fed_counts), key="bar_fed")

with col_insight:
    st.markdown("#### Hallazgo")
    st.info(
        "**Solo 10 países** concentran más del **50 %** de todos los "
        "jugadores del mundo.\n\n"
        "India y Rusia lideran con ~9 % cada una, seguidas de "
        "Francia (6.8 %) y España (5.7 %).\n\n"
        "Impulsados por programas nacionales de ajedrez escolar y una "
        "fuerte tradición competitiva."
    )
    st.markdown("---")
    st.markdown("#### Nota metodológica")
    st.caption(
        "Ranking por **volumen absoluto**. Países con alta cultura "
        "ajedrecística per cápita (Armenia, Islandia, Georgia) no "
        "aparecen aquí."
    )

st.divider()

# ── Sección 3 — Mapa Natural Earth ────────────────────────────────────────────
st.markdown("### Distribución mundial de jugadores")
st.caption(
    "Escala logarítmica · Proyección Robinson · "
    "Pasa el cursor sobre un país para ver el detalle exacto."
)

map_data = get_world_map_data()
st.plotly_chart(fig_map_world(map_data), key="map_world")

st.divider()

# ── Sección 4 — Tabla resumen ─────────────────────────────────────────────────
st.markdown(f"### Tabla detallada — Top {TOP_N} federaciones")


st.dataframe(
    fed_counts[["#", "Federación", "Jugadores", "% del mundial", "Acumulado %"]],
    column_config={
        "Jugadores": st.column_config.NumberColumn(format="%d"),
        "% del mundial": st.column_config.ProgressColumn(
            format="%.1f %%",
            min_value=0,
            max_value=15,
        ),
        "Acumulado %": st.column_config.NumberColumn(format="%.1f %%"),
    },
    hide_index=True,
    key="table_fed",
)
st.caption(
    "Top federaciones con barras de progreso relativas (% del mundial) y porcentaje acumulado."
)

