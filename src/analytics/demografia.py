"""
src/analytics/demografia_federacion.py
======================================
Estudio demográfico y estructural de una federación del padrón FIDE:
volumen de jugadores, género, categorías formativas, perfiles de ritmo y títulos.
"""

from typing import Optional
import numpy as np
import pandas as pd

from src.config.constants import (
    CAT_ORDER,
    MAX_ACTIVE_AGE,
    PRO_ORDER,
    TITLE_NAMES,
    TITLE_ORDER,
    YOUTH_CATS,
)

REQUIRED_DEMOGRAPHIC_COLS = {
    "fideid", "country", "sex", "title", "edad", "categoria", "player_profile",
}


def _pct(num: float, den: float, decimals: int = 1) -> float:
    return np.round(num / den * 100, decimals) if den > 0 else 0.0


class DemografiaFederacion:
    """
    Analizador demográfico de una federación (o del padrón global si `fed=None`).

    Uso: `DemografiaFederacion(df, "COL").kpis_demograficos()`
    """

    def __init__(self, df: pd.DataFrame, fed: Optional[str] = None, max_age: int = MAX_ACTIVE_AGE):
        missing = REQUIRED_DEMOGRAPHIC_COLS - set(df.columns)
        if missing:
            raise ValueError(
                f"El DataFrame no contiene las columnas requeridas: {sorted(missing)}"
            )

        self.fed = fed.strip().upper() if fed else None
        self.max_age = max_age

        if self.fed is not None:
            mask = (df["country"] == self.fed) & (df["edad"] <= max_age)
        else:
            mask = df["edad"] <= max_age
        self.df: pd.DataFrame = df.loc[mask].copy()

        if self.df.empty:
            raise ValueError(
                f"La federación '{self.fed}' no tiene registros con edad <= {max_age}."
            )

    def kpis_demograficos(self) -> pd.DataFrame:
        """Resumen general con valores absolutos (`cantidad`) y relativos (`porcentaje`)."""
        df = self.df
        n_reg = len(df)

        youth = df[df["categoria"].isin(YOUTH_CATS)]
        adult = df[df["categoria"] == "Absoluta"]
        n_titulados = int((df["title"] != "nt").sum())

        cantidad = {
            "registrados": n_reg,
            "hombres": int((df["sex"] == "M").sum()),
            "mujeres": int((df["sex"] == "F").sum()),
            "juveniles": len(youth),
            "adultos": len(adult),
            "mujeres_juveniles": int((youth["sex"] == "F").sum()),
            "mujeres_adultas": int((adult["sex"] == "F").sum()),
            "titulados": n_titulados,
            "sin_titulo": n_reg - n_titulados,
        }
        if "activo_mes" in df.columns:
            cantidad["activos_mes"] = int(df["activo_mes"].sum())

        # Denominador de cada porcentaje (por defecto, el total de registrados)
        denominadores = {
            "mujeres_juveniles": cantidad["juveniles"],
            "mujeres_adultas": cantidad["adultos"],
        }
        porcentaje = {
            k: _pct(v, denominadores.get(k, n_reg), 2) for k, v in cantidad.items()
        }

        out = pd.DataFrame({"cantidad": cantidad, "porcentaje": porcentaje})
        out.index.name = "indicador"
        return out

    def resumen_demografico(self) -> pd.DataFrame:
        """Desglose por categoría: registrados, género, % femenino y edad mediana."""
        df = self.df

        sex_ct = (
            df.groupby(["categoria", "sex"], observed=False)
            .size()
            .unstack(fill_value=0)
            .reindex(index=CAT_ORDER, columns=["M", "F"], fill_value=0)
        )

        out = pd.DataFrame(index=pd.Index(CAT_ORDER, name="categoria"))
        out["registrados"] = (
            df.groupby("categoria", observed=False)["fideid"]
            .count()
            .reindex(CAT_ORDER, fill_value=0)
        )
        out["M"] = sex_ct["M"]
        out["F"] = sex_ct["F"]
        out["pct_F"] = (out["F"] / (out["M"] + out["F"]).replace(0, np.nan) * 100).round(1).fillna(0.0)
        out["edad_mediana"] = (
            df.groupby("categoria", observed=False)["edad"]
            .median()
            .reindex(CAT_ORDER)
            .round(1)
        )
        return out.reset_index()

    def resumen_perfiles(self) -> pd.DataFrame:
        """Distribución de perfiles de ritmo de juego (`player_profile`)."""
        counts = self.df["player_profile"].value_counts().reindex(PRO_ORDER, fill_value=0)
        return pd.DataFrame({
            "player_profile": PRO_ORDER,
            "jugadores": counts.values,
            "pct": (counts.values / len(self.df) * 100).round(1),
        })

    def resumen_titulos(self) -> pd.DataFrame:
        """Desglose de títulos oficiales FIDE por género."""
        titled_order = [t for t in TITLE_ORDER if t != "nt"][::-1]
        sub = self.df[self.df["title"].isin(titled_order)]

        cols = ["title", "nombre_titulo", "M", "F", "total", "pct_titulados"]
        if sub.empty:
            return pd.DataFrame(columns=cols)

        ct = (
            sub.groupby(["title", "sex"], observed=False)
            .size()
            .unstack(fill_value=0)
            .reindex(index=titled_order, columns=["M", "F"], fill_value=0)
        )

        out = ct.copy()
        out["total"] = out["M"] + out["F"]
        out["pct_titulados"] = (out["total"] / out["total"].sum() * 100).round(1)
        out["nombre_titulo"] = out.index.map(TITLE_NAMES)
        out.index.name = "title"

        return out.loc[out["total"] > 0, cols[1:]].reset_index()


Demografia = DemografiaFederacion