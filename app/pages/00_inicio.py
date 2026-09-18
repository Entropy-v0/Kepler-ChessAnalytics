"""
Página 0 — Inicio
=================
Introducción y cifras hero del padrón oficial FIDE.
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from components.kpis import render_global_kpis
from components.theme import render_page_header
from service.data_loader import load_active_players, load_all_players

# ── Encabezado ─────────────────────────────────────────────────────────────────
render_page_header(
    "Kepler ChessAnalytic",
    "Descubrimientos del padrón oficial FIDE — ~1.9 millones de registros mundiales",
)

st.markdown(
    "La **Federación Internacional de Ajedrez (FIDE)** publica mensualmente el padrón "
    "completo de jugadores registrados en todo el mundo. "
    "Esta plataforma traduce ese volumen masivo de datos en **ventanas interactivas de descubrimiento**: "
    "dónde se concentra el ajedrez mundial, cómo se distribuyen los ratings Elo, qué brechas demográficas "
    "y de género existen, cómo madura la cantera juvenil y qué particularidades presenta el ajedrez en Venezuela."
)

st.divider()

# ── Cifras hero del padrón ─────────────────────────────────────────────────────
st.markdown("### El padrón mundial en cifras")
try:
    df_all = load_all_players()
    df_active = load_active_players()
    render_global_kpis(df_all, df_active)
except Exception:
    pass

st.divider()

# ── Tarjetas de navegación ─────────────────────────────────────────────────────
st.markdown("### Ventanas de descubrimiento")

col1, col2 = st.columns(2)

with col1:
    st.info(
        "**Panorama Global**  \n"
        "Concentración geográfica absoluta y mapa mundial interactivo.\n\n"
        ":material/public: *Explorar federaciones*"
    )
    st.info(
        "**Distribución de Elo**  \n"
        "Densidad multimodal (Clásico, Rápido, Blitz) y pirámide de títulos de élite.\n\n"
        ":material/bar_chart: *Explorar ratings y títulos*"
    )
    st.info(
        "**Demografía y Género**  \n"
        "Brecha de participación, pirámide poblacional por categorías y deserción juvenil.\n\n"
        ":material/groups: *Explorar demografía*"
    )

with col2:
    st.info(
        "**Cohortes Juveniles**  \n"
        "Curva biológica de desarrollo de nivel y canteras líderes del mundo.\n\n"
        ":material/child_care: *Explorar ajedrez joven*"
    )
    st.info(
        "**Venezuela**  \n"
        "Radiografía nacional: el dominio del ritmo rápido y blitz, ranking y cantera.\n\n"
        ":material/flag: *Explorar ajedrez venezolano*"
    )

st.markdown("---")
st.caption(
    "Padrón oficial FIDE · Proyecto Kepler ChessAnalytic · Arquitectura de datos columnar en Parquet"
)
