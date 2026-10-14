"""
src/utils/snapshot.py
=====================
Utilidad para resolver el período (snapshot) de una corrida del pipeline
y construir las rutas particionadas asociadas.
"""

from datetime import date, datetime
from pathlib import Path
from typing import Optional
from src.config.settings import DATA_RAW_DIR, DATA_INTERIM_DIR, DATA_PROCESSED_DIR, INTERIM_FILENAME


def resolve_snapshot(value: Optional[str] = None) -> date:
    """
    Retorna el primer día del mes del snapshot.

    Args:
        value: Cadena 'YYYY-MM' (p. ej. '2026-10'). Si es None, usa el mes actual.
    """
    if value is None:
        return date.today().replace(day=1)
    try:
        return datetime.strptime(value, "%Y-%m").date()
    except ValueError:
        raise ValueError(f"Snapshot inválido '{value}'. Formato esperado: YYYY-MM")


def snapshot_label(snapshot: date) -> str:
    """'2026-10' a partir de date(2026, 10, 1)."""
    return snapshot.strftime("%Y-%m")


def raw_dir(snapshot: date) -> Path:
    return DATA_RAW_DIR / snapshot_label(snapshot)


def interim_path(snapshot: date) -> Path:
    return DATA_INTERIM_DIR / f"snapshot_date={snapshot.isoformat()}" / INTERIM_FILENAME


def processed_dir(snapshot: date) -> Path:
    return DATA_PROCESSED_DIR / f"snapshot_date={snapshot.isoformat()}"


def latest_snapshot(base_dir: Path = DATA_PROCESSED_DIR) -> date:
    """Devuelve el snapshot más reciente que exista en processed/."""
    parts = sorted(base_dir.glob("snapshot_date=*"))
    if not parts:
        raise FileNotFoundError(f"No hay snapshots en {base_dir}. Ejecute primero la fase de procesamiento.")
    return date.fromisoformat(parts[-1].name.split("=")[1])