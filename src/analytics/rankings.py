"""
src/analytics/rankings.py
=========================
Estudio general de rankings, distribuciones de Elo, correlaciones entre modalidades
y posicionamiento por percentiles (nacional y mundial) / Z-Score robusto.
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.config.constants import (
    CAT_ORDER,
    MAX_ACTIVE_AGE,
    MODALIDADES_MAP,
    RATING_COLS,
)

REQUIRED_RANKING_COLS = {
    "fideid",
    "country",
    "sex",
    "edad",
    "categoria",
    *RATING_COLS,
}


class Rankings:
    """
    Analizador general de rendimiento Elo, correlaciones entre ritmos y tablas de percentiles.

    Puede instanciarse para una federación específica (`Rankings(df, "COL")`)
    o sobre el padrón global (`Rankings(df)`).
    """

    def __init__(
        self,
        df: pd.DataFrame,
        fed: Optional[str] = None,
        max_age: int = MAX_ACTIVE_AGE,
    ):
        missing = REQUIRED_RANKING_COLS - set(df.columns)
        if missing:
            raise ValueError(
                f"El DataFrame no contiene las columnas de ranking requeridas: {sorted(missing)}"
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

    def comparativa_elo(self) -> pd.DataFrame:
        """
        Compara cobertura, mediana, rango intercuartílico (IQR) y P90 en los
        tres ritmos oficiales (Clásico, Rápido, Blitz) frente al padrón mundial.
        """
        scope = self.df_scope
        world = self.df
        n_scope = max(len(scope), 1)

        rows: List[Dict[str, Any]] = []
        for col, label in MODALIDADES_MAP.items():
            s_fed = scope[col].dropna().astype(float)
            s_fed = s_fed[s_fed > 0]

            s_world = world[col].dropna().astype(float)
            s_world = s_world[s_world > 0]

            med_fed = float(s_fed.median()) if len(s_fed) > 0 else np.nan
            q25_fed = float(s_fed.quantile(0.25)) if len(s_fed) > 0 else np.nan
            q75_fed = float(s_fed.quantile(0.75)) if len(s_fed) > 0 else np.nan
            p90_fed = float(s_fed.quantile(0.90)) if len(s_fed) > 0 else np.nan
            med_world = float(s_world.median()) if len(s_world) > 0 else np.nan

            rows.append({
                "modalidad": label,
                "columna": col,
                "jugadores": int(len(s_fed)),
                "cobertura_pct": round(len(s_fed) / n_scope * 100, 1),
                "mediana": round(med_fed, 0) if pd.notna(med_fed) else np.nan,
                "iqr": round(q75_fed - q25_fed, 0) if pd.notna(med_fed) else np.nan,
                "p90": round(p90_fed, 0) if pd.notna(p90_fed) else np.nan,
                "mediana_mundial": round(med_world, 0) if pd.notna(med_world) else np.nan,
                "diferencia_mediana": (
                    round(med_fed - med_world, 0)
                    if pd.notna(med_fed) and pd.notna(med_world)
                    else np.nan
                ),
            })

        return pd.DataFrame(rows)

    def curvas_por_categoria(self) -> pd.DataFrame:
        """
        Evolución de medianas de Elo (Clásico, Rápido y Blitz) e IQR clásico
        a través de las categorías oficiales FIDE (Sub 8 a Absoluta).
        """
        scope = self.df_scope
        rows: List[Dict[str, Any]] = []

        for cat in CAT_ORDER:
            sub = scope[scope["categoria"] == cat]
            rc = sub["rating"].dropna().astype(float)
            rc = rc[rc > 0]
            rr = sub["rapid_rating"].dropna().astype(float)
            rr = rr[rr > 0]
            rb = sub["blitz_rating"].dropna().astype(float)
            rb = rb[rb > 0]

            rows.append({
                "categoria": cat,
                "n_clasico": int(len(rc)),
                "mediana_clasico": round(float(rc.median()), 0) if len(rc) > 0 else np.nan,
                "p25_clasico": round(float(rc.quantile(0.25)), 0) if len(rc) > 0 else np.nan,
                "p75_clasico": round(float(rc.quantile(0.75)), 0) if len(rc) > 0 else np.nan,
                "p90_clasico": round(float(rc.quantile(0.90)), 0) if len(rc) > 0 else np.nan,
                "mediana_rapido": round(float(rr.median()), 0) if len(rr) > 0 else np.nan,
                "mediana_blitz": round(float(rb.median()), 0) if len(rb) > 0 else np.nan,
            })

        return pd.DataFrame(rows)

    def correlacion_ritmos(self, solo_completos: bool = False) -> pd.DataFrame:
        """
        Calcula la matriz de correlación entre `rating`, `rapid_rating` y `blitz_rating`.
        Si `solo_completos=True`, filtra únicamente a los jugadores con los 3 ratings (> 0).
        """
        scope = self.df_scope
        elos = scope[list(RATING_COLS)].astype(float)
        if solo_completos:
            elos = elos.dropna()
        return elos.corr().round(3)

    def ranking_y_percentiles(
        self,
        modalidad: str = "rating",
        categoria: Optional[str] = None,
        sex: Optional[str] = None,
        top_n: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Calcula para cada jugador del alcance seleccionado:
        - `percentil_nacional`: percentil (0-100) dentro de su categoría y país.
        - `percentil_mundial`: percentil (0-100) dentro de su categoría a nivel mundial.
        - `z_score_local`: Z-Score robusto basado en IQR de su categoría y país
          (con fallback al IQR mundial si la muestra local < 5 o IQR == 0).
        - `gap_rapido_clasico`: diferencia `rapid_rating - rating`.
        """
        if modalidad not in RATING_COLS:
            raise ValueError(f"Modalidad inválida '{modalidad}'. Use una de {RATING_COLS}.")

        world = self.df.copy()
        world_valid = world[world[modalidad].notna() & (world[modalidad] > 0)].copy()
        if world_valid.empty:
            return pd.DataFrame()

        world_valid[modalidad] = world_valid[modalidad].astype(float)

        world_valid["percentil_mundial"] = (
            world_valid.groupby("categoria", observed=True)[modalidad].rank(pct=True) * 100
        ).round(1)
        med_global = world_valid.groupby("categoria", observed=True)[modalidad].transform("median")
        q1_global = world_valid.groupby("categoria", observed=True)[modalidad].transform(
            lambda x: x.quantile(0.25)
        )
        q3_global = world_valid.groupby("categoria", observed=True)[modalidad].transform(
            lambda x: x.quantile(0.75)
        )
        iqr_global = q3_global - q1_global

        target_df = (
            world_valid[world_valid["country"] == self.fed].copy()
            if self.fed is not None
            else world_valid
        )
        if target_df.empty:
            return pd.DataFrame()

        idx = target_df.index
        grp_cols = ["categoria", "country"]
        target_df["percentil_nacional"] = (
            target_df.groupby(grp_cols, observed=True)[modalidad].rank(pct=True) * 100
        ).round(1)

        med_local = target_df.groupby(grp_cols, observed=True)[modalidad].transform("median")
        q1_local = target_df.groupby(grp_cols, observed=True)[modalidad].transform(
            lambda x: x.quantile(0.25)
        )
        q3_local = target_df.groupby(grp_cols, observed=True)[modalidad].transform(
            lambda x: x.quantile(0.75)
        )
        iqr_local = q3_local - q1_local
        n_local = target_df.groupby(grp_cols, observed=True)[modalidad].transform("count")

        fallback = (iqr_local == 0) | (n_local < 5)
        med_eff = med_local.mask(fallback, med_global.loc[idx])
        iqr_eff = iqr_local.mask(fallback, iqr_global.loc[idx])

        target_df["z_score_local"] = ((target_df[modalidad] - med_eff) / (iqr_eff + 1e-5)).round(2)
        target_df["gap_rapido_clasico"] = (
            target_df["rapid_rating"].astype("Float64") - target_df["rating"].astype("Float64")
        )

        if categoria is not None:
            target_df = target_df[target_df["categoria"] == categoria]
        if sex is not None:
            target_df = target_df[target_df["sex"] == sex.upper()]

        target_df = target_df.sort_values(
            by=[modalidad, "fideid"], ascending=[False, True]
        ).reset_index(drop=True)
        if top_n is not None:
            target_df = target_df.head(top_n)

        cols_order = [
            "fideid",
            "name",
            "country",
            "sex",
            "edad",
            "categoria",
            "title",
            "player_profile",
            *RATING_COLS,
            "gap_rapido_clasico",
            "percentil_nacional",
            "percentil_mundial",
            "z_score_local",
        ]
        existing_cols = [c for c in cols_order if c in target_df.columns]
        return target_df[existing_cols]
