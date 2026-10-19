"""
src/config/constants.py
========================
Constantes de negocio, clasificaciones FIDE y diccionarios de mapeo geográfico.
"""

from typing import Dict, List, Optional, Tuple


RATING_COLS: Tuple[str, ...] = ("rating", "rapid_rating", "blitz_rating")
GAMES_COLS: Tuple[str, ...] = ("games", "rapid_games", "blitz_games")
MODALIDADES_MAP: Dict[str, str] = {
    "rating": "Clásico",
    "rapid_rating": "Rápido",
    "blitz_rating": "Blitz",
}

TITLES_COLUMNS: List[str] = ["title", "w_title", "o_title"]
INACTIVE_FLAGS: Tuple[str, ...] = ("i", "wi")
MIN_BIRTH_YEAR: int = 1920
MAX_ACTIVE_AGE: int = 97

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

# Listas ordenadas derivadas directamente de las reglas (sin redundancia)
CAT_ORDER: List[str] = list(AGE_CATEGORY_RULES.values())
YOUTH_CATS: List[str] = [c for c in CAT_ORDER if c != "Absoluta"]
PRO_ORDER: List[str] = list(PLAYER_PROFILE_RULES.values())

# ── Jerarquía y Nombres de Títulos Oficiales FIDE ──────────────────────────────
TITLES_ELITE: List[str] = ["GM", "IM", "WGM", "FM", "WIM", "CM", "WFM", "WCM"]
TITLES_OPEN_TOP: List[str] = ["GM", "IM", "FM"]
TITLE_WOMAN: List[str] = [t for t in TITLES_ELITE if t.startswith("W")]
TITLE_ORDER: List[str] = ["nt"] + TITLES_ELITE[::-1]

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

# ── Mapeo de Códigos FIDE a ISO-3 ──────────────────────────────────────────────
FIDE_TO_ISO3: Dict[str, str] = {
    "ENG": "GBR", "SCO": "GBR", "WAL": "GBR", "NIR": "GBR",
    "IRI": "IRN", "GER": "DEU", "SUI": "CHE", "NED": "NLD",
    "CRO": "HRV", "RSA": "ZAF", "PHI": "PHL", "MAS": "MYS",
    "SIN": "SGP", "VIE": "VNM", "TPE": "TWN", "UAE": "ARE",
    "GUA": "GTM", "PAR": "PRY", "BOL": "BOL", "ECU": "ECU",
    "HAI": "HTI", "DOM": "DOM", "TTO": "TTO", "BAR": "BRB",
}
