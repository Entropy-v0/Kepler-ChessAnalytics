"""
components/kpis.py
==================
Widgets reutilizables para mostrar métricas destacadas (KPI cards).
"""

import pandas as pd
import streamlit as st


def metric_card(label: str, value: str, delta: str | None = None, help: str | None = None) -> None:
    """
    Renderiza una métrica individual con st.metric.

    Args:
        label: Título de la métrica.
        value: Valor principal a mostrar.
        delta: Cambio o comparación opcional (aparece en verde/rojo).
        help: Texto explicativo en tooltip.
    """
    st.metric(label=label, value=value, delta=delta, help=help)


def render_global_kpis(df_kpis: pd.DataFrame) -> None:
    """
    Muestra las 4 métricas globales principales en una fila de columnas
    consumiendo directamente el Data Mart precalculado (Capa Oro).

    Args:
        df_kpis: DataFrame unifilar con métricas precalculadas (mart_kpis_globales).
    """
    row = df_kpis.iloc[0]
    total_players = int(row["total_players"])
    active_players = int(row["active_players"])
    total_countries = int(row["total_countries"])
    pct_active = f"{active_players / total_players * 100:.1f}%"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Jugadores en el padrón",
            f"{total_players:,}".replace(",", "."),
            help="Total de jugadores con al menos un rating > 0 y fecha de nacimiento válida.",
        )
    with c2:
        metric_card(
            "Jugadores activos",
            f"{active_players:,}".replace(",", "."),
            help="Jugadores sin flag de inactividad FIDE.",
        )
    with c3:
        metric_card(
            "Federaciones representadas",
            str(total_countries),
            help="Número de países/federaciones con al menos un jugador registrado.",
        )
    with c4:
        metric_card(
            "Tasa de actividad",
            pct_active,
            help="Porcentaje de jugadores del padrón que están activos.",
        )
