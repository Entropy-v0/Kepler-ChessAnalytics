"""
src/config/constants.py
========================
Constantes de negocio, clasificaciones FIDE y diccionarios de mapeo geográfico.
"""

from typing import Dict, List, Optional, Tuple


TITLES_COLUMNS: List[str] = ["title", "w_title", "o_title"]
MIN_BIRTH_YEAR: int = 1920

# ── Reglas de Categorías por Edad ──────────────────────────────────────────────
AGE_CATEGORY_RULES: Dict[Tuple[int, Optional[int]], str] = {
    (0, 8): "Sub 8",
    (8, 10): "Sub 10",
    (10, 12): "Sub 12",
    (12, 14): "Sub 14",
    (14, 16): "Sub 16",
    (16, 18): "Sub 18",
    (18, 20): "Sub 20",
    (20, None): "Absoluta",
}

# ── Reglas de Perfil de Jugador (Ritmos FIDE) ──────────────────────────────────
# Estructura: (has_classic, has_rapid, has_blitz) -> perfil
PLAYER_PROFILE_RULES: Dict[Tuple[bool, bool, bool], str] = {
    (True, True, True): "completo",
    (True, False, False): "especialista_clasico",
    (False, True, False): "especialista_rapido",
    (False, False, True): "especialista_blitz",
    (True, True, False): "clasico_rapido",
    (True, False, True): "clasico_blitz",
    (False, True, True): "rapido_blitz",
}

# Listas ordenadas derivadas directamente del orden de los diccionarios
CAT_ORDER: List[str] = list(AGE_CATEGORY_RULES.values())
PRO_ORDER: List[str] = list(PLAYER_PROFILE_RULES.values())


YOUTH_CATS: List[str] = [
    "Sub 8", "Sub 10", "Sub 12", "Sub 14",
    "Sub 16", "Sub 18", "Sub 20"
]

TITLES_ELITE: List[str] = ["GM", "IM", "WGM", "FM", "WIM", "CM", "WFM", "WCM"]

TITLE_WOMAN: List[str] =  ["WGM", "WIM", "WFM", "WCM"]

TITLE_NAMES: Dict[str, str] = {
    "GM": "Gran Maestro",
    "IM": "Maestro Internacional",
    "FM": "Maestro FIDE",
    "CM": "Candidato a Maestro",
    "WGM": "WGM",
    "WIM": "WIM",
    "WFM": "WFM",
    "WCM": "WCM",
    "nt": "Sin título",
}

FIDE_TO_ISO3: Dict[str, str] = {
    "ENG": "GBR", "SCO": "GBR", "WAL": "GBR", "NIR": "GBR",
    "IRI": "IRN", "GER": "DEU", "SUI": "CHE", "NED": "NLD",
    "CRO": "HRV", "RSA": "ZAF", "PHI": "PHL", "MAS": "MYS",
    "SIN": "SGP", "VIE": "VNM", "TPE": "TWN", "UAE": "ARE",
    "GUA": "GTM", "PAR": "PRY", "BOL": "BOL", "ECU": "ECU",
    "HAI": "HTI", "DOM": "DOM", "TTO": "TTO", "BAR": "BRB",
}
