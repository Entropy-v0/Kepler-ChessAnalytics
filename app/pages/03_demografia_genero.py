"""
Página 3 — Demografía y Género
================================
Descubrimiento: La brecha invisible del ajedrez mundial y la estructura por categorías.
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from components.charts import (
    fig_line_gender_drop,
    fig_parity_federations,
    fig_pyramid_ages,
    fig_pyramid_categories,
    fig_stacked_gender_federations,
)
from components.theme import render_page_header
from service.demographics_service import (
    get_age_quinquennial_pyramid,
    get_demographic_kpis,
    get_fide_categories_gender,
    get_gender_parity_top_countries,
    get_top_federations_gender_ratio,
)

# ── Encabezado ─────────────────────────────────────────────────────────────────
render_page_header("Demografía y Género", "La brecha de participación y la estructura etaria del padrón activo")

st.markdown(
    "El padrón de jugadores activos de la **FIDE** (~437 K registros) permite radiografiar "
    "la composición demográfica del ajedrez competitivo: la proporción entre hombres y mujeres, "
    "la relevancia de las categorías formativas y cómo varía la brecha entre federaciones."
)
st.divider()

# ── Sección 1 — KPIs demográficos ─────────────────────────────────────────────
st.markdown("### El padrón demográfico en cifras")
kpis = get_demographic_kpis()

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Jugadores masculinos",
    f"{kpis['pct_m']:.1f} %",
    f"{kpis['n_m']:,} jugadores",
    help="Total de jugadores masculinos activos.",
)
c2.metric(
    "Jugadoras femeninas",
    f"{kpis['pct_f']:.1f} %",
    f"{kpis['n_f']:,} jugadoras",
    help="Total de jugadoras femeninas activas en el padrón mundial.",
)
c3.metric(
    "Cantera juvenil (Sub-20)",
    f"{kpis['pct_youth']:.1f} %",
    f"{kpis['n_youth']:,} jóvenes",
    help="Porcentaje del padrón activo que pertenece a categorías juveniles (Sub 8 a Sub 20).",
)
c4.metric(
    "Presencia Femenina: Juvenil vs Adulta",
    f"{kpis['pct_f_youth']:.1f} % vs {kpis['pct_f_adult']:.1f} %",
    f"–{kpis['drop_pp']:.1f} pp de caída",
    help="Porcentaje de mujeres en categorías juveniles comparado con categoría Absoluta.",
)

st.divider()

# ── Sección 2 — Barras apiladas: proporción por país ──────────────────────────
TOP_N = 20
st.markdown(f"### Proporción de género en el Top {TOP_N} de federaciones")
st.caption("Federaciones con mayor número absoluto de jugadores activos.")

fed_sex = get_top_federations_gender_ratio(top_n=TOP_N)
fig_stack = fig_stacked_gender_federations(fed_sex)
st.plotly_chart(fig_stack, key="stack_fed_sex")

st.divider()

# ── Sección 3 — Pirámide y estructura etaria / categorías ─────────────────────
st.markdown("### Estructura poblacional por género")
st.caption("Explora la pirámide por Categorías oficiales FIDE o por Grupos de edad quinquenales.")

view_type = st.radio(
    "Seleccionar nivel de agregación:",
    ["Categorías Oficiales FIDE (Sub-8 a Sub-20 y Absoluta)", "Rangos de Edad Quinquenales (0–4 a 95+)"],
    horizontal=True,
    key="view_pyramid_type",
)

if "Categorías" in view_type:
    cat_df = get_fide_categories_gender()
    fig_pyr = fig_pyramid_categories(cat_df)
    st.plotly_chart(fig_pyr, key="pyramid_categories")
else:
    pyramid_age = get_age_quinquennial_pyramid()
    fig_pyr = fig_pyramid_ages(pyramid_age)
    st.plotly_chart(fig_pyr, key="pyramid_ages")

# ── Sección 4 — La deserción juvenil femenina ─────────────────────────────────
st.markdown("### La brecha generacional: Cuota femenina por cohorte")

col_trend, col_insight = st.columns([3, 1])

cat_df = get_fide_categories_gender()

with col_trend:
    fig_line = fig_line_gender_drop(cat_df, kpis["pct_f"])
    st.plotly_chart(fig_line, key="trend_pct_f")

with col_insight:
    st.markdown("#### Hallazgo clave")
    st.info(
        "En categorías escolares infantiles (**Sub-8 a Sub-14**), la presencia de "
        "niñas supera el **18 %**.\n\n"
        "Sin embargo, a partir de **Sub-16** comienza una deserción progresiva "
        "que se agrava en **Sub-20 (13.1 %)** y colapsa en la categoría "
        "**Absoluta a solo 5.5 %**.\n\n"
        "La brecha de género no surge en la niñez, sino en la transición "
        "a la vida adulta."
    )

st.divider()

# ── Sección 5 — Paridad por federación ────────────────────────────────────────
st.markdown("### Federaciones con mayor paridad de género")
st.caption("Federaciones con al menos 500 jugadores activos. Ordenadas por % femenino.")

best_parity = get_gender_parity_top_countries(min_players=500, top_n=12)
fig_parity = fig_parity_federations(best_parity, kpis["pct_f"])
st.plotly_chart(fig_parity, key="parity_fed")
st.info(
    "**Mongolia** lidera con un **31.2 %** de jugadoras activas — más del triple "
    "que la media mundial (9.6 %). Le siguen **Sri Lanka (26.2 %)**, **Turkmenistán (26.1 %)** "
    "y **China (24.6 %)**."
)
