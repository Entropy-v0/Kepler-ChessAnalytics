"""
tests/conftest.py
=================
Configuración de entorno de pruebas para Kepler-ChessAnalitic.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))
