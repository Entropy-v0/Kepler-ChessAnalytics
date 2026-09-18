"""
src/config/constants.py
========================
Constantes de negocio, clasificaciones FIDE y diccionarios de mapeo geográfico.
"""

from typing import Dict, List

CAT_ORDER: List[str] = [
    "Sub 8", "Sub 10", "Sub 12", "Sub 14",
    "Sub 16", "Sub 18", "Sub 20", "Absoluta"
]

YOUTH_CATS: List[str] = [
    "Sub 8", "Sub 10", "Sub 12", "Sub 14",
    "Sub 16", "Sub 18", "Sub 20"
]

TITLES_ELITE: List[str] = ["GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM"]

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
