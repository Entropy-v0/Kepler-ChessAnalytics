"""
src/analytics/demografia.py
===========================
Estudio demográfico y estructural general del padrón FIDE (global o por federación).
Analiza volumen de jugadores registrados, distribución por género, categorías formativas,
perfiles de ritmo de juego y estructura de títulos.
"""

from typing import Any, Dict, Iterable, List, Optional

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
    "fideid",
    "country",
    "sex",
    "title",
    "edad",
    "categoria",
    "player_profile",
}


class Demografia:
    """
    Analizador demográfico y estructural general del padrón FIDE.

    Puede instanciarse para una federación específica (`Demografia(df, "COL")`)
    o sobre el padrón global (`Demografia(df)`).
    """

    def __init__(
        self,
        df: pd.DataFrame,
        fed: Optional[str] = None,
        max_age: int = MAX_ACTIVE_AGE,
    ):
        missing = REQUIRED_DEMOGRAPHIC_COLS - set(df.columns)
        if missing:
            raise ValueError(
                f"El DataFrame no contiene las columnas demográficas requeridas: {sorted(missing)}"
            )

        self.max_age = max_age
        self.df: pd.DataFrame = df.loc[df["edad"] <= self.max_age].copy()
        self.fed = fed.strip().upper() if fed else None

        if self.fed is not None:
            mask_fed = self.df["country"] == self.fed
            if not mask_fed.any():
                raise ValueError(f"La federación '{self.fed}' no tiene registros en el DataFrame.")
            self.df_scope: pd.DataFrame = self.df.loc[mask_fed]
        else:
            self.df_scope = self.df

    def kpis_demograficos(self) -> pd.DataFrame:
        """
        Devuelve un DataFrame resumen general con valores absolutos (`cantidad`)
        y relativos (`porcentaje`).
        """
        scope = self.df_scope
        n_reg = int(len(scope))

        n_m = int((scope["sex"] == "M").sum())
        n_f = int((scope["sex"] == "F").sum())

        youth = scope[scope["categoria"].isin(YOUTH_CATS)]
        adult = scope[scope["categoria"] == "Absoluta"]

        n_youth = int(len(youth))
        n_adult = int(len(adult))
        n_f_youth = int((youth["sex"] == "F").sum())
        n_f_adult = int((adult["sex"] == "F").sum())

        n_titulados = int((scope["title"] != "nt").sum())
        n_sin_titulo = n_reg - n_titulados

        def _pct(num: int, den: int, decimals: int = 1) -> float:
            return round(num / den * 100, decimals) if den > 0 else 0.0

        data = {
            "cantidad": {
                "registrados": n_reg,
                "hombres": n_m,
                "mujeres": n_f,
                "juveniles": n_youth,
                "adultos": n_adult,
                "mujeres_juveniles": n_f_youth,
                "mujeres_adultas": n_f_adult,
                "titulados": n_titulados,
                "sin_titulo": n_sin_titulo,
            },
            "porcentaje": {
                "registrados": 100.0 if n_reg > 0 else 0.0,
                "hombres": _pct(n_m, n_reg),
                "mujeres": _pct(n_f, n_reg),
                "juveniles": _pct(n_youth, n_reg),
                "adultos": _pct(n_adult, n_reg),
                "mujeres_juveniles": _pct(n_f_youth, n_youth),
                "mujeres_adultas": _pct(n_f_adult, n_adult),
                "titulados": _pct(n_titulados, n_reg, 2),
                "sin_titulo": _pct(n_sin_titulo, n_reg, 2),
            },
        }
        df_kpis = pd.DataFrame(data)
        df_kpis.index.name = "indicador"
        return df_kpis

    def resumen_demografico(self) -> pd.DataFrame:
        """
        Desglose por categoría FIDE (Sub 8 a Absoluta) con total de registrados,
        conteo por género, porcentaje femenino y edad mediana.
        """
        scope = self.df_scope

        reg_ct = (
            scope.groupby("categoria", observed=False)["fideid"]
            .count()
            .reindex(CAT_ORDER, fill_value=0)
        )

        sex_ct = (
            scope.groupby(["categoria", "sex"], observed=False)
            .size()
            .unstack(fill_value=0)
            .reindex(CAT_ORDER, fill_value=0)
        )
        for col in ("M", "F"):
            if col not in sex_ct.columns:
                sex_ct[col] = 0

        edad_med = (
            scope.groupby("categoria", observed=False)["edad"]
            .median()
            .reindex(CAT_ORDER)
            .round(1)
        )

        out = pd.DataFrame(index=CAT_ORDER)
        out.index.name = "categoria"
        out["registrados"] = reg_ct.astype(int)
        out["M"] = sex_ct["M"].astype(int)
        out["F"] = sex_ct["F"].astype(int)
        total_scope = (out["M"] + out["F"]).replace(0, np.nan)
        out["pct_F"] = (out["F"] / total_scope * 100).round(1).fillna(0.0)
        out["edad_mediana"] = edad_med

        return out.reset_index()

    demografic_resumen = resumen_demografico

    def resumen_perfiles(self) -> pd.DataFrame:
        """
        Compara la distribución de perfiles de ritmo de juego (`player_profile`)
        del alcance seleccionado frente al padrón mundial.
        """
        scope = self.df_scope
        world = self.df

        fed_counts = scope["player_profile"].value_counts().reindex(PRO_ORDER, fill_value=0)
        world_counts = world["player_profile"].value_counts().reindex(PRO_ORDER, fill_value=0)

        fed_total = max(len(scope), 1)
        world_total = max(len(world), 1)

        out = pd.DataFrame({
            "player_profile": PRO_ORDER,
            "jugadores": fed_counts.values.astype(int),
            "pct_alcance": (fed_counts.values / fed_total * 100).round(1),
            "pct_mundial": (world_counts.values / world_total * 100).round(1),
        })
        out["diferencia_pp"] = (out["pct_alcance"] - out["pct_mundial"]).round(1)
        return out

    def resumen_titulos(self) -> pd.DataFrame:
        """Desglose de títulos oficiales FIDE por género."""
        scope = self.df_scope
        titled_order = [t for t in TITLE_ORDER if t != "nt"]

        sub = scope[scope["title"].isin(titled_order)]
        if sub.empty:
            return pd.DataFrame(
                columns=["title", "nombre_titulo", "M", "F", "total", "pct_titulados"]
            )

        ct = (
            sub.groupby(["title", "sex"], observed=False)
            .size()
            .unstack(fill_value=0)
            .reindex(titled_order[::-1], fill_value=0)
        )
        for col in ("M", "F"):
            if col not in ct.columns:
                ct[col] = 0

        out = pd.DataFrame(index=titled_order[::-1])
        out.index.name = "title"
        out["nombre_titulo"] = out.index.map(TITLE_NAMES)
        out["M"] = ct["M"].astype(int)
        out["F"] = ct["F"].astype(int)
        out["total"] = out["M"] + out["F"]
        total_tit = max(int(out["total"].sum()), 1)
        out["pct_titulados"] = (out["total"] / total_tit * 100).round(1)

        return out[out["total"] > 0].reset_index()

    @classmethod
    def comparar_federaciones(
        cls, df: pd.DataFrame, feds: Iterable[str], max_age: int = MAX_ACTIVE_AGE
    ) -> pd.DataFrame:
        """
        Genera una matriz comparativa demográfica y estructural para una lista de federaciones.
        """
        rows: List[Dict[str, Any]] = []
        for fed_code in feds:
            analyzer = cls(df, fed_code, max_age=max_age)
            kpis = analyzer.kpis_demograficos()
            cant = kpis["cantidad"]
            pct = kpis["porcentaje"]
            edad_med = (
                float(analyzer.df_scope["edad"].median())
                if len(analyzer.df_scope) > 0
                else np.nan
            )
            prof_df = analyzer.resumen_perfiles().sort_values("jugadores", ascending=False)
            perfil_dom = prof_df.iloc[0]["player_profile"] if not prof_df.empty else "sin_elo"
            pct_dom = float(prof_df.iloc[0]["pct_alcance"]) if not prof_df.empty else 0.0

            rows.append({
                "country": analyzer.fed,
                "registrados": int(cant["registrados"]),
                "edad_mediana": edad_med,
                "juveniles": int(cant["juveniles"]),
                "pct_juveniles": float(pct["juveniles"]),
                "mujeres": int(cant["mujeres"]),
                "pct_mujeres": float(pct["mujeres"]),
                "pct_f_juvenil": float(pct["mujeres_juveniles"]),
                "pct_f_adulta": float(pct["mujeres_adultas"]),
                "drop_femenino_pp": round(
                    float(pct["mujeres_juveniles"] - pct["mujeres_adultas"]), 1
                ),
                "titulados": int(cant["titulados"]),
                "pct_titulados": float(pct["titulados"]),
                "perfil_dominante": perfil_dom,
                "pct_perfil_dominante": pct_dom,
            })

        return pd.DataFrame(rows)
