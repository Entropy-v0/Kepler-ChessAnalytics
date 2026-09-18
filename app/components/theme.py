"""
app/components/theme.py
========================
Constantes de diseño, paleta de colores y helpers de estilización unificados.
"""

from typing import Any, Dict, List, Optional
import plotly.graph_objects as go
import streamlit as st

# ── Paleta de Colores Principal ────────────────────────────────────────────────
C_NAVY = "#1E3A5F"         # Azul marino profundo (Clásico / Masculino / Primario)
C_BLUE = "#2E86AB"         # Azul medio (Rápido / Secundario)
C_RED = "#E84855"          # Rojo coral (Femenino / Alertas)
C_AMBER = "#F39C12"        # Ámbar / Dorado (Blitz / Destacados)
C_LIGHT_BLUE = "#4A7BB5"   # Azul claro (Barras / Rellenos)
C_MUTED = "#94A3B8"        # Gris tenue (Rejillas / Textos secundarios)
C_DARK_TEXT = "#1C2333"    # Texto oscuro principal

# ── Mapeo de Colores para Títulos FIDE ──────────────────────────────────────────
TITLE_COLORS: Dict[str, str] = {
    "Gran Maestro": "#1E3A5F",
    "Gran Maestro (GM)": "#1E3A5F",
    "Maestro Internacional": "#2E86AB",
    "Maestro Internacional (IM)": "#2E86AB",
    "Maestro FIDE": "#4A7BB5",
    "Maestro FIDE (FM)": "#4A7BB5",
    "Candidato a Maestro": "#90CAF9",
    "Candidato a Maestro (CM)": "#90CAF9",
    "WGM": "#C0392B",
    "WIM": "#E84855",
    "Maestra Internacional Fem. (WIM)": "#E84855",
    "WFM": "#F1948A",
    "Maestra FIDE Fem. (WFM)": "#F1948A",
    "WCM": "#FADBD8",
    "Candidata a Maestra (WCM)": "#FADBD8",
}

# ── Categorías FIDE Estándar ───────────────────────────────────────────────────
CAT_ORDER: List[str] = ["Sub 8", "Sub 10", "Sub 12", "Sub 14", "Sub 16", "Sub 18", "Sub 20", "Absoluta"]
YOUTH_CATS: List[str] = ["Sub 8", "Sub 10", "Sub 12", "Sub 14", "Sub 16", "Sub 18", "Sub 20"]

# ── Mapeo de Códigos de Países FIDE a ISO-3 ───────────────────────────────────
FIDE_TO_ISO3: Dict[str, str] = {
    "ENG": "GBR", "SCO": "GBR", "WAL": "GBR", "NIR": "GBR",
    "IRI": "IRN", "GER": "DEU", "SUI": "CHE", "NED": "NLD",
    "CRO": "HRV", "RSA": "ZAF", "PHI": "PHL", "MAS": "MYS",
    "SIN": "SGP", "VIE": "VNM", "TPE": "TWN", "UAE": "ARE",
    "GUA": "GTM", "PAR": "PRY", "BOL": "BOL", "ECU": "ECU",
    "HAI": "HTI", "DOM": "DOM", "TTO": "TTO", "BAR": "BRB",
}


def render_page_header(title: str, subtitle: str) -> None:
    """Renderiza el encabezado estándar con estilos unificados para todas las páginas."""
    st.markdown(
        f"""
        <h1 style='font-size: 2.2rem; font-weight: 700; color: {C_DARK_TEXT}; margin-bottom: 4px;'>
            {title}
        </h1>
        <p style='color: #64748B; font-size: 1.1rem; margin-top: 0; margin-bottom: 16px;'>
            {subtitle}
        </p>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_theme(
    fig: go.Figure,
    height: int = 380,
    margin: Optional[Dict[str, int]] = None,
    showlegend: bool = True,
    hovermode: Optional[str] = None,
) -> go.Figure:
    """
    Aplica el tema visual estandarizado del proyecto Kepler a cualquier gráfico de Plotly.
    """
    if margin is None:
        margin = dict(l=10, r=10, t=10, b=10)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=margin,
        showlegend=showlegend,
        font=dict(color=C_DARK_TEXT, family="sans-serif"),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.06)",
            zerolinecolor="rgba(0,0,0,0.12)",
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.06)",
            zerolinecolor="rgba(0,0,0,0.12)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    if hovermode:
        fig.update_layout(hovermode=hovermode)

    return fig
