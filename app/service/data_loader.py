"""
app/service/data_loader.py
===========================
Carga e ingesta de datos en formato Parquet con caché de Streamlit.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

_ROOT = Path(__file__).resolve().parent.parent.parent
_PROCESSED = _ROOT / "data" / "processed"
_DATA_WEB = _ROOT / "data" / "dataWeb"


@st.cache_data(show_spinner="Cargando datos globales…")
def load_all_players() -> pd.DataFrame:
    """Dataset completo de jugadores FIDE (~776K)."""
    return pd.read_parquet(_PROCESSED / "fide_players_all.parquet")


@st.cache_data(show_spinner="Cargando jugadores activos…")
def load_active_players() -> pd.DataFrame:
    """Subconjunto de jugadores activos sin bandera de inactividad (~437K)."""
    return pd.read_parquet(_PROCESSED / "fide_players_active.parquet")


@st.cache_data(show_spinner="Cargando datos Venezuela…")
def load_venezuela_players() -> pd.DataFrame:
    """Jugadores venezolanos registrados en la FIDE (~3K)."""
    return pd.read_parquet(_DATA_WEB / "jugadores_ajedrez_VEN.parquet")


@st.cache_data(show_spinner="Cargando demografía por países…")
def load_country_demographics() -> pd.DataFrame:
    """Demografía agregada por país/federación."""
    return pd.read_parquet(_DATA_WEB / "demografia_paises.parquet")


@st.cache_data(show_spinner="Cargando categorías juveniles…")
def load_youth_categories() -> pd.DataFrame:
    """Categorías juveniles por federación."""
    return pd.read_parquet(_DATA_WEB / "cateogrias_juveniles_fed.parquet")
