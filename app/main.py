"""
Kepler ChessAnalytic — Dashboard Web
=====================================
Orquestador principal y enrutador de navegación con st.navigation.
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from components.sidebar import render_sidebar_header, render_sidebar_footer

st.set_page_config(
    page_title="Kepler ChessAnalytic",
    page_icon=":material/chess:",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("pages/00_inicio.py", title="Inicio", icon=":material/home:", default=True),
    st.Page("pages/01_panorama_global.py", title="Panorama Global", icon=":material/public:"),
    st.Page("pages/02_distribucion_elo.py", title="Distribución de Elo", icon=":material/bar_chart:"),
    st.Page("pages/03_demografia_genero.py", title="Demografía y Género", icon=":material/groups:"),
    st.Page("pages/04_cohortes_juveniles.py", title="Cohortes Juveniles", icon=":material/child_care:"),
    st.Page("pages/05_venezuela.py", title="Venezuela", icon=":material/flag:"),
]


pg = st.navigation(pages, position="hidden")

render_sidebar_header()

with st.sidebar:
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)


    for page in pages:
        st.page_link(page)
        
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

render_sidebar_footer()

pg.run()