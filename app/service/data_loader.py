"""
app/service/data_loader.py
===========================
Carga e ingesta de datos en formato Parquet desde la Capa Oro (data/marts/)
con optimización de caché en Streamlit (@st.cache_data).
"""

from pathlib import Path
import pandas as pd
import streamlit as st

_ROOT = Path(__file__).resolve().parent.parent.parent
_MARTS = _ROOT / "data" / "marts"
_PROCESSED = _ROOT / "data" / "processed"


# ── Panorama Global (Página 01) ────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando KPIs globales…")
def load_global_kpis_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_kpis_globales.parquet")


@st.cache_data(show_spinner="Cargando panorama global…")
def load_panorama_global_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_panorama_global.parquet")


# ── Distribución de Elo y Títulos (Página 02) ──────────────────────────────────
@st.cache_data(show_spinner="Cargando KPIs de Elo…")
def load_elo_kpis_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_elo_kpis.parquet")


@st.cache_data(show_spinner="Cargando densidades KDE…")
def load_kde_ratings_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_kde_ratings.parquet")


@st.cache_data(show_spinner="Cargando ratings clásicos…")
def load_ratings_clasico_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_ratings_clasico.parquet")


@st.cache_data(show_spinner="Cargando histograma clásico…")
def load_histograma_clasico_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_histograma_clasico.parquet")



@st.cache_data(show_spinner="Cargando resumen de títulos…")
def load_titulos_resumen_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_titulos_resumen.parquet")


@st.cache_data(show_spinner="Cargando matriz de títulos…")
def load_titulos_federacion_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_titulos_federacion.parquet")


# ── Demografía y Género (Página 03) ───────────────────────────────────────────
@st.cache_data(show_spinner="Cargando demografía…")
def load_demografia_kpis_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_demografia_kpis.parquet")


@st.cache_data(show_spinner="Cargando federaciones por género…")
def load_demografia_federaciones_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_demografia_federaciones.parquet")


@st.cache_data(show_spinner="Cargando categorías FIDE…")
def load_demografia_categorias_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_demografia_categorias.parquet")


@st.cache_data(show_spinner="Cargando pirámide etaria…")
def load_demografia_piramide_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_demografia_piramide.parquet")


@st.cache_data(show_spinner="Cargando paridad de género…")
def load_demografia_paridad_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_demografia_paridad.parquet")


# ── Cohortes Juveniles (Página 04) ─────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando KPIs juveniles…")
def load_youth_kpis_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_youth_kpis.parquet")


@st.cache_data(show_spinner="Cargando categorías juveniles…")
def load_youth_categorias_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_youth_categorias.parquet")


@st.cache_data(show_spinner="Cargando curvas de nivel…")
def load_youth_elo_curves_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_youth_elo_curves.parquet")


@st.cache_data(show_spinner="Cargando canteras mundiales…")
def load_youth_canteras_matriz_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_youth_canteras_matriz.parquet")


# ── Venezuela (Página 05) ──────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos Venezuela…")
def load_venezuela_players() -> pd.DataFrame:
    """Jugadores venezolanos registrados en la FIDE (~3K)."""
    return pd.read_parquet(_MARTS / "mart_venezuela.parquet")


@st.cache_data(show_spinner="Cargando comparativa mundial…")
def load_venezuela_comparativa_mart() -> pd.DataFrame:
    return pd.read_parquet(_MARTS / "mart_venezuela_comparativa.parquet")


# ── Compatibilidad con loaders legados (si son requeridos) ────────────────────
@st.cache_data(show_spinner="Cargando datos globales maestro…")
def load_all_players() -> pd.DataFrame:
    """Dataset completo maestro de jugadores FIDE (~776K)."""
    return pd.read_parquet(_PROCESSED / "fide_players_all.parquet")


@st.cache_data(show_spinner="Cargando jugadores activos maestro…")
def load_active_players() -> pd.DataFrame:
    """Subconjunto maestro de jugadores activos (~437K)."""
    return pd.read_parquet(_PROCESSED / "fide_players_active.parquet")
