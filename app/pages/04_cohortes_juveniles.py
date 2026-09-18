"""
Página 4 — Cohortes Juveniles
================================
Descubrimiento: El ajedrez joven, curvas biológicas de rendimiento y canteras mundiales.
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from components.charts import (
    fig_cantera_pct,
    fig_cantera_vol,
    fig_youth_categories,
    fig_youth_elo_bands,
    fig_youth_elo_curves,
)
from components.theme import render_page_header
from service.youth_service import (
    get_youth_canteras_summary,
    get_youth_categories_breakdown,
    get_youth_elo_curves_data,
    get_youth_kpis,
)

# ── Encabezado ─────────────────────────────────────────────────────────────────
render_page_header(
    "Cohortes Juveniles",
    "El ajedrez joven: progresión biológica de nivel y canteras mundiales",
)

st.markdown(
    "Las categorías oficiales FIDE (desde **Sub-8** hasta **Sub-20**) concentran a las nuevas "
    "generaciones de ajedrecistas. A través de ellas se puede observar el desarrollo "
    "de la fuerza competitiva y el mapa de inversión formativa entre naciones."
)
st.divider()

# ── Sección 1 — KPIs Juveniles ────────────────────────────────────────────────
st.markdown("### La cantera mundial en cifras")
kpis = get_youth_kpis()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Total jugadores juveniles",
    f"{kpis['total_youth']:,}",
    help="Jugadores activos en categorías Sub-8 a Sub-20.",
)
c2.metric(
    "Cuota juvenil del padrón",
    f"{kpis['pct_youth_global']:.1f} %",
    "de los activos mundiales",
    help="Casi 4 de cada 10 jugadores federados activos compiten en categorías formativas.",
)
c3.metric(
    "Categoría más poblada",
    f"{kpis['peak_cat']}",
    f"{kpis['peak_count']:,} jóvenes",
    help="Sub-16 es el pico de volumen competitivo juvenil en la FIDE.",
)
c4.metric(
    "Desarrollo de Elo (Sub 8 ➔ Sub 20)",
    f"+{kpis['elo_diff']} pts",
    "en mediana Clásica",
    help="Incremento en la mediana del rating Clásico desde Sub-8 hasta Sub-20.",
)

st.divider()

# ── Sección 2 — Volumen de jugadores por categoría ────────────────────────────
st.markdown("### Volumen de jugadores por categoría formativa")
st.caption("Distribución por cohorte FIDE con desglose entre hombres y mujeres.")

cat_summary = get_youth_categories_breakdown()
fig_cat = fig_youth_categories(cat_summary)
st.plotly_chart(fig_cat, key="bar_youth_categories")

st.divider()

# ── Sección 3 — Curva biológica de Elo en los 3 ritmos ─────────────────────────
st.markdown("### Curva de desarrollo de Elo por cohorte")
st.caption("Evolución de la mediana de Elo en partidas Clásicas, Rápidas y Blitz.")

df_elo = get_youth_elo_curves_data()

col_curve, col_box = st.columns([3, 2])

with col_curve:
    fig_curve = fig_youth_elo_curves(df_elo)
    st.plotly_chart(fig_curve, key="curve_elo_modalities")

with col_box:
    st.markdown("#### Banda de rendimiento Clásico")
    st.caption("Rango intercuartílico (P25 a P75) y techo de élite (P99).")
    fig_bands = fig_youth_elo_bands(df_elo)
    st.plotly_chart(fig_bands, key="bands_elo_classic")

st.info(
    "Entre **Sub-8 y Sub-14**, el Elo progresa de forma gradual (~15 puntos por categoría). "
    "A partir de **Sub-14**, la curva de rating clásico se dispara (+170 puntos hasta Sub-20), "
    "marcando el periodo de consolidación táctica y madurez en partidas de ritmo clásico."
)

st.divider()

# ── Sección 4 — Canteras mundiales ────────────────────────────────────────────
st.markdown("### Canteras mundiales: ¿Quién lidera el recambio generacional?")

top_cantera_pct, top_cantera_vol = get_youth_canteras_summary()

col_pct, col_vol = st.columns(2)

with col_pct:
    st.markdown("#### Países con mayor proporción de juveniles")
    st.caption("Porcentaje de jugadores menores de 20 años sobre el total federado activo (mínimo 1.000 jugadores).")
    fig_pct = fig_cantera_pct(top_cantera_pct, kpis["pct_youth_global"])
    st.plotly_chart(fig_pct, key="cantera_pct_chart")

with col_vol:
    st.markdown("#### Países con mayor volumen absoluto de juveniles")
    st.caption("Total de jugadores registrados en categorías Sub-8 a Sub-20.")
    fig_vol = fig_cantera_vol(top_cantera_vol)
    st.plotly_chart(fig_vol, key="cantera_vol_chart")

st.caption(
    "🇮🇳 **India** es la superpotencia de cantera absoluta con **22.338** jóvenes compitiendo, "
    "representando el 63.9 % de todos sus jugadores activos. En Asia (Vietnam, China, Sri Lanka), "
    "más del 75 % del padrón ajedrecístico es menor de edad, contrastando fuertemente "
    "con Europa donde la mayoría de los jugadores supera los 20 años."
)
