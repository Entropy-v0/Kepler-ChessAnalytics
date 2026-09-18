"""
components/sidebar.py
=====================
Componentes modulares para renderizar una barra lateral enriquecida.
"""

import streamlit as st

def render_sidebar_header() -> None:
    """Renderiza el branding principal arriba del menú de navegación."""
    with st.sidebar:
        st.markdown(
            """
            <div style='
                padding: 2px 0 14px 0; 
                width: 100%; 
                box-sizing: border-box; 
                overflow-wrap: break-word;
            '>
                <div style='
                    font-size: 1.65rem;
                    font-weight: 800;
                    color: #1E3A5F;
                    letter-spacing: -0.6px;
                    line-height: 1.1;
                '>
                    Kepler Chess
                </div>
                <div style='
                    font-size: 0.78rem;
                    font-weight: 700;
                    color: #64748B;
                    letter-spacing: 1.2px;
                    margin-top: 4px;
                    text-transform: uppercase;
                '>
                    FIDE Census Intelligence
                </div>
                <div style='margin-top: 8px;'>
                    <span style='
                        background-color: #E2E8F0;
                        color: #334155;
                        font-size: 0.72rem;
                        font-weight: 600;
                        padding: 2px 8px;
                        border-radius: 10px;
                        display: inline-block;
                    '>
                        Snapshot Oficial 2026
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar_footer() -> None:
    """Renderiza las métricas y créditos debajo del menú de navegación."""
    with st.sidebar:
        st.divider()

        st.markdown(
            """
            <div style='
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 10px 12px;
                margin-top: 2px;
                margin-bottom: 12px;
                width: 100%;
                box-sizing: border-box;
                overflow: hidden;
            '>
                <div style='
                    font-size: 0.72rem;
                    font-weight: 700;
                    color: #64748B;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 6px;
                '>
                    Padrón mundial activo
                </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Padrón total", "776.2 K", help="Jugadores registrados con Elo > 0.")
            st.metric("Federaciones", "207", help="Países con al menos un jugador en el padrón.")
        with c2:
            st.metric("Activos", "437.2 K", help="Jugadores sin bandera de inactividad federativa.")
            st.metric("GMs en mundo", "1 899", help="Jugadores en el planeta con título de Gran Maestro.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()

        st.markdown(
            """
            <div style='
                font-size: 0.75rem; 
                color: #94A3B8; 
                line-height: 1.5; 
                padding-top: 4px;
                width: 100%;
                box-sizing: border-box;
                overflow-wrap: break-word;
            '>
                <div><b>Fuente oficial:</b> FIDE Ratings</div>
                <div><b>Pipeline:</b> Kepler ChessAnalytic</div>
                <div><b>Autor:</b> Christian Deliso Ure (entropyV0)</div>
                <div>Motor columnar Parquet</div>
            </div>
            """,
            unsafe_allow_html=True,
        )