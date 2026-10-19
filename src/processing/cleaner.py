"""
src/processing/cleaner.py
=========================
Limpieza determinista del padrón FIDE.
Devuelve las filas conservadas y, aparte, las rechazadas con la regla que las descartó.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger

from src.config.constants import (
    GAMES_COLS,
    MIN_BIRTH_YEAR,
    RATING_COLS,
    TITLE_ORDER,
    TITLE_WOMAN,
    TITLES_COLUMNS,
)

REQUIRED_COLS = {"fideid", "birthday", *RATING_COLS}
REJECT_KEEP_COLS = ("fideid", "country")  # lo mínimo para auditar sesgo geográfico


@dataclass(frozen=True)
class Rule:
    name: str
    rejects: Callable[[pd.DataFrame], pd.Series]  # True = la fila se descarta


@dataclass(frozen=True)
class CleanResult:
    clean: pd.DataFrame
    rejected: pd.DataFrame  # columnas: fideid, country, rule
    input_rows: int

    def rejections_by_rule(self) -> Dict[str, int]:
        counts = self.rejected["rule"].value_counts()
        return {k: int(v) for k, v in counts.items() if v > 0}


class DataCleaner:
    """Aplica reglas de calidad en orden fijo. Cada fila rechazada se atribuye a la primera regla que falla."""

    def __init__(self, reference_year: Optional[int] = None, min_birth_year: int = MIN_BIRTH_YEAR):
        self.reference_year = reference_year or datetime.now().year
        self.min_birth_year = min_birth_year
        # edad >= 1: coherente con el primer bin de categorías y evita edad <= 0
        self.max_birth_year = self.reference_year - 1
        self.rules: Tuple[Rule, ...] = (
            Rule("sin_rating", lambda d: ~(d[list(RATING_COLS)].fillna(0) > 0).any(axis=1)),
            Rule("sin_birthday", lambda d: d["birthday"].isna()),
            Rule("birthday_anomalo", lambda d: d["birthday"] < self.min_birth_year),
            Rule("birthday_futuro", lambda d: d["birthday"] > self.max_birth_year),
            # va al final: solo compara filas que ya pasaron el resto
            Rule("duplicado", lambda d: d.duplicated(subset="fideid", keep="first")),
        )

    def clean(self, df: pd.DataFrame) -> CleanResult:
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            raise ValueError(f"Columnas obligatorias ausentes en el raw: {sorted(missing)}")

        input_rows = len(df)
        logger.info(f"Iniciando limpieza. Registros de entrada: {input_rows:,}")

        remaining, rejected_parts = df, []
        for rule in self.rules:
            mask = rule.rejects(remaining).fillna(False).to_numpy(dtype=bool)
            if mask.any():
                cols = [c for c in REJECT_KEEP_COLS if c in remaining.columns]
                rejected_parts.append(remaining.loc[mask, cols].assign(rule=rule.name))
            remaining = remaining.loc[~mask]

        rule_names = [r.name for r in self.rules]
        rejected = (
            pd.concat(rejected_parts, ignore_index=True)
            if rejected_parts
            else pd.DataFrame(columns=[*REJECT_KEEP_COLS, "rule"])
        )
        rejected["fideid"] = rejected["fideid"].astype(str)
        rejected["rule"] = pd.Categorical(rejected["rule"], categories=rule_names, ordered=True)

        clean = self._normalize(remaining)

        assert len(clean) + len(rejected) == input_rows, "Las filas no cuadran: entrada != limpias + rechazadas"
        assert clean["fideid"].is_unique

        result = CleanResult(clean=clean, rejected=rejected, input_rows=input_rows)
        logger.success(f"Limpieza completada: {len(clean):,} conservadas | rechazos: {result.rejections_by_rule()}")
        return result

    @staticmethod
    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        """Transforma solo las filas que sobrevivieron a los filtros."""
        out = df.copy()
        out["fideid"] = out["fideid"].astype(str)
        for col in RATING_COLS:
            out[col] = pd.to_numeric(out[col], errors="coerce")
            out[col] = out[col].where(out[col] > 0).astype("Int16")  # 0 -> NA
        for col in GAMES_COLS:
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype("int16")
        out["birthday"] = out["birthday"].astype("int16")  # ya sin nulos

        for col in TITLES_COLUMNS:
            if col in out.columns:
                out[col] = out[col].fillna("nt").replace("", "nt")
            else:
                out[col] = "nt"

        # Fusión jerárquica de title y w_title conservando el título de mayor rango
        t = pd.Categorical(out["title"], categories=TITLE_ORDER, ordered=True)
        w = pd.Categorical(out["w_title"], categories=TITLE_ORDER, ordered=True)
        codigos = np.maximum(t.codes, w.codes)
        out["title"] = pd.Categorical.from_codes(codigos, categories=TITLE_ORDER, ordered=True)
        out = out.drop(columns=["w_title"])

        # Corrección de anomalías de género: jugadoras con título femenino registradas como 'M'
        if "sex" in out.columns:
            anomalia_sex = (out["sex"] == "M") & (out["title"].isin(TITLE_WOMAN))
            if anomalia_sex.any():
                if isinstance(out["sex"].dtype, pd.CategoricalDtype) and "F" not in out["sex"].cat.categories:
                    out["sex"] = out["sex"].cat.add_categories(["F"])
                out.loc[anomalia_sex, "sex"] = "F"

        if "flag" in out.columns:
            out = out.drop(columns=["flag"])

        return out

