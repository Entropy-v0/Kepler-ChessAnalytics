"""
tests/test_services.py
======================
Pruebas automatizadas de integración para los servicios analíticos de app/service/.
Verifica que cada función de servicio retorne los datos y tipos esperados consumiendo la Capa Oro.
"""

import pandas as pd
import numpy as np
from app.service.global_service import (
    get_global_kpis,
    get_top_federations_summary,
    get_world_map_data,
)
from app.service.elo_service import (
    get_elo_kpis,
    get_kde_data,
    get_classic_ratings_series,
    get_title_structure_summary,
    get_titles_heatmap_data,
)
from app.service.demographics_service import (
    get_demographic_kpis,
    get_top_federations_gender_ratio,
    get_fide_categories_gender,
    get_age_quinquennial_pyramid,
    get_gender_parity_top_countries,
)
from app.service.youth_service import (
    get_youth_kpis,
    get_youth_categories_breakdown,
    get_youth_elo_curves_data,
    get_youth_canteras_summary,
)
from app.service.venezuela_service import (
    get_venezuela_kpis,
    get_venezuela_elo_comparison,
    get_venezuela_titles_summary,
    get_top_venezuelan_players,
    get_venezuela_youth_breakdown,
)


def test_global_service():
    kpis = get_global_kpis()
    assert "total_players" in kpis and kpis["total_players"] > 0
    assert "active_players" in kpis and kpis["active_players"] > 0
    assert "total_countries" in kpis and kpis["total_countries"] > 0

    fed_counts, top_n = get_top_federations_summary(top_n=15)
    assert len(fed_counts) == 15
    assert list(fed_counts.columns) == ["#", "Federación", "Jugadores", "% del mundial", "Acumulado %"]

    map_data = get_world_map_data()
    assert len(map_data) > 0
    assert "country" in map_data.columns
    assert "log_jugadores" in map_data.columns


def test_elo_service():
    elo_kpis = get_elo_kpis()
    assert elo_kpis["p50"] > 1000
    assert elo_kpis["mean"] > 1000
    assert elo_kpis["p99"] > elo_kpis["p50"]

    kde_results, p50, y_p50 = get_kde_data()
    assert len(kde_results) == 3
    assert p50 == elo_kpis["p50"]
    assert y_p50 > 0

    ratings = get_classic_ratings_series()
    assert len(ratings) > 100000

    from app.service.elo_service import get_classic_histogram_data
    from app.components.charts import fig_hist_classic_percentiles
    hist_df, max_rating = get_classic_histogram_data()
    assert len(hist_df) == 74
    assert "bin_center" in hist_df.columns
    assert "count" in hist_df.columns
    assert max_rating > 2800

    percs = {"P50": (elo_kpis["p50"], "#E84855")}
    fig = fig_hist_classic_percentiles(hist_df, percs)
    fig_json = fig.to_json()
    assert len(fig_json) < 20000  # Payload debe ser < 20 KB (antes era 3 MB)


    title_kpis, titled_df = get_title_structure_summary()
    assert "titulados_n" in title_kpis
    assert len(titled_df) > 0

    heat = get_titles_heatmap_data(top_feds_n=12)
    assert len(heat) == 12
    assert "GM" in heat.columns


def test_demographics_service():
    demo_kpis = get_demographic_kpis()
    assert demo_kpis["pct_m"] + demo_kpis["pct_f"] > 99.0
    assert demo_kpis["n_youth"] > 0

    ratio = get_top_federations_gender_ratio(top_n=20)
    assert len(ratio) <= 20
    assert "pct_F" in ratio.columns

    cats = get_fide_categories_gender()
    assert len(cats) == 8
    assert "Sub 8" in cats["categoria"].values

    pyr = get_age_quinquennial_pyramid()
    assert len(pyr) > 0
    assert "age_bin" in pyr.columns

    parity = get_gender_parity_top_countries(min_players=500, top_n=12)
    assert len(parity) <= 12


def test_youth_service():
    youth_kpis = get_youth_kpis()
    assert youth_kpis["total_youth"] > 0
    assert youth_kpis["pct_youth_global"] > 0

    cats = get_youth_categories_breakdown()
    assert len(cats) == 7
    assert "Sub 20" in cats["categoria"].values

    curves = get_youth_elo_curves_data()
    assert len(curves) == 7
    assert "classic_med" in curves.columns

    cantera_pct, cantera_vol = get_youth_canteras_summary()
    assert len(cantera_pct) == 10
    assert len(cantera_vol) == 10


def test_venezuela_service():
    ven_kpis = get_venezuela_kpis()
    assert ven_kpis["total_ven"] > 0
    assert ven_kpis["n_gm"] >= 0

    rc, rr, rb, comp = get_venezuela_elo_comparison()
    assert len(comp) == 3
    assert "Diferencia" in comp.columns

    titles_kpis, titles_bar = get_venezuela_titles_summary()
    assert titles_kpis["total_ven"] > 0
    assert len(titles_bar) > 0

    top_ven = get_top_venezuelan_players("Clásico", "Todas", "Todos", "Todos")
    assert len(top_ven) == 20
    assert "Elo Clásico" in top_ven.columns

    ven_youth = get_venezuela_youth_breakdown()
    assert len(ven_youth) == 8


def test_cached_charts():
    """Verifica que las funciones de gráficos cacheadas devuelvan objetos Figure válidos."""
    from app.service.global_service import get_world_map_data
    from app.components.charts import fig_map_world, fig_venezuela_modalities

    map_data = get_world_map_data()
    fig1 = fig_map_world(map_data)
    assert fig1 is not None
    assert hasattr(fig1, "to_plotly_json")

    fig2 = fig_venezuela_modalities(100, 200, 300, 1000)
    assert fig2 is not None
    assert hasattr(fig2, "to_plotly_json")

