"""
components package
==================
Componentes de UI y visualización modulares y reutilizables para Kepler ChessAnalytic.
"""

from .kpis import metric_card, render_global_kpis
from .sidebar import render_sidebar_header, render_sidebar_footer

__all__ = ["metric_card", "render_global_kpis", "render_sidebar"]
