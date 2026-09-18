"""
app/components/charts.py
========================
Funciones de visualización reutilizables para toda la aplicación Kepler ChessAnalytic.
Cada función devuelve un objeto Plotly Figure listo para renderizar con st.plotly_chart().
"""

from typing import Any, Dict, List, Tuple, Union
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


from components.theme import (
    C_AMBER,
    C_BLUE,
    C_LIGHT_BLUE,
    C_MUTED,
    C_NAVY,
    C_RED,
    TITLE_COLORS,
    apply_plotly_theme,
)


@st.cache_data
def fig_bar_top_federations(fed_counts: pd.DataFrame) -> go.Figure:
    """Barras horizontales del Top N federaciones por volumen de jugadores."""
    fig = px.bar(
        fed_counts.sort_values("Jugadores"),
        x="Jugadores",
        y="Federación",
        orientation="h",
        text="Jugadores",
        color="Jugadores",
        color_continuous_scale=[
            [0.0, "#C8D8EC"],
            [0.5, "#4A7BB5"],
            [1.0, "#1E3A5F"],
        ],
        labels={"Jugadores": "Jugadores registrados", "Federación": ""},
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, yaxis=dict(tickfont_size=13))
    return apply_plotly_theme(fig, height=500, margin=dict(l=10, r=60, t=10, b=10))


@st.cache_data
def fig_map_world(map_data: pd.DataFrame) -> go.Figure:
    """Mapa de coropletas Natural Earth (Proyección Robinson)."""
    fig = go.Figure(
        go.Choropleth(
            locations=map_data["country"],
            z=map_data["log_jugadores"],
            text=map_data["country"],
            customdata=map_data[["Jugadores_fmt", "country"]].values,
            hovertemplate="<b>%{customdata[1]}</b><br>Jugadores: %{customdata[0]}<extra></extra>",
            locationmode="ISO-3",
            colorscale=[
                [0.00, "#EBF2FB"],
                [0.25, "#A8C8E8"],
                [0.50, "#4A7BB5"],
                [0.75, "#1E3A5F"],
                [1.00, "#0A1628"],
            ],
            zmin=0,
            zmax=map_data["log_jugadores"].max(),
            marker_line_color="#FFFFFF",
            marker_line_width=0.5,
            colorbar=dict(
                title=dict(text="Jugadores", font=dict(color="#1C2333", size=12)),
                tickvals=[1, 2, 3, 4, 5],
                ticktext=["10", "100", "1 K", "10 K", "100 K"],
                tickfont=dict(color="#1C2333"),
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="#CBD5E0",
                borderwidth=1,
                len=0.7,
                thickness=14,
            ),
        )
    )
    fig.update_layout(
        geo=dict(
            projection_type="robinson",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#94A3B8",
            coastlinewidth=0.6,
            showland=True,
            landcolor="#EDF2F7",
            showocean=True,
            oceancolor="#BFD7ED",
            showlakes=True,
            lakecolor="#BFD7ED",
            showcountries=True,
            countrycolor="#CBD5E0",
            countrywidth=0.4,
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return apply_plotly_theme(fig, height=500, margin=dict(l=0, r=0, t=0, b=0))


@st.cache_data
def fig_kde_modalities(
    kde_curves: List[Tuple[str, List[float], List[float]]],
    p50_classic: int,
    y_p50_classic: float,
) -> go.Figure:
    """KDE comparativo de densidad para Clásico, Rápido y Blitz."""
    colors = {"Clásico": C_NAVY, "Rápido": C_BLUE, "Blitz": C_RED}
    fills = {
        "Clásico": "rgba(30,58,95,0.12)",
        "Rápido": "rgba(46,134,171,0.12)",
        "Blitz": "rgba(232,72,85,0.12)",
    }

    fig = go.Figure()
    for name, x_grid, y in kde_curves:
        fig.add_trace(
            go.Scatter(
                x=x_grid,
                y=y,
                mode="lines",
                name=name,
                line=dict(color=colors.get(name, C_NAVY), width=2.5),
                fill="tozeroy",
                fillcolor=fills.get(name, "rgba(30,58,95,0.12)"),
                hovertemplate=f"<b>{name}</b><br>Rating: %{{x:.0f}}<br>Densidad: %{{y:.5f}}<extra></extra>",
            )
        )

    fig.add_shape(
        type="line",
        x0=p50_classic,
        x1=p50_classic,
        y0=0,
        y1=y_p50_classic,
        line=dict(color=C_NAVY, width=1.5, dash="dot"),
    )
    fig.add_annotation(
        x=p50_classic,
        y=y_p50_classic,
        text=f"Mediana Clásico<br>{p50_classic:,}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=C_NAVY,
        font=dict(size=11, color=C_NAVY),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor=C_NAVY,
        ax=40,
        ay=-30,
    )
    fig.update_layout(
        xaxis=dict(
            title="Rating Elo",
            range=[1380, 2860],
            tickmode="linear",
            dtick=200,
        ),
        yaxis=dict(title="Densidad"),
    )
    return apply_plotly_theme(fig, height=380, hovermode="x unified")


@st.cache_data
def fig_hist_classic_percentiles(
    hist_data: Union[pd.DataFrame, pd.Series, List[float]],
    percs: Dict[str, Tuple[int, str]],
) -> go.Figure:
    """
    Histograma de Rating Clásico con anotaciones de percentiles.
    Optimizado con go.Bar sobre bins precalculados (reduce el payload JSON de 3 MB a 1.8 KB).
    """
    if isinstance(hist_data, pd.DataFrame) and "bin_center" in hist_data.columns:
        x_vals = hist_data["bin_center"].values
        y_vals = hist_data["count"].values
    else:
        # Fallback de compatibilidad si se proporciona una Serie o lista de valores brutos
        raw_vals = np.asarray(hist_data, dtype=float)
        raw_vals = raw_vals[~np.isnan(raw_vals)]
        bins = np.arange(1400, 2880 + 20, 20)
        y_vals, bin_edges = np.histogram(raw_vals, bins=bins)
        x_vals = (bin_edges[:-1] + bin_edges[1:]) / 2

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x_vals,
            y=y_vals,
            marker_color=C_LIGHT_BLUE,
            marker_line_color=C_NAVY,
            marker_line_width=0.4,
            opacity=0.85,
            name="Jugadores",
            hovertemplate="Rating: %{x:.0f}<br>Jugadores: %{y:,}<extra></extra>",
        )
    )

    max_y = float(np.max(y_vals)) * 1.15 if len(y_vals) > 0 and np.max(y_vals) > 0 else 1000.0
    for label, (val, color) in percs.items():
        fig.add_shape(
            type="line",
            x0=val,
            x1=val,
            y0=0,
            y1=max_y,
            line=dict(color=color, width=1.6, dash="dash"),
        )
        fig.add_annotation(
            x=val,
            y=max_y,
            text=f"<b>{label}</b><br>{val:,}",
            showarrow=False,
            font=dict(size=9, color=color),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor=color,
            borderwidth=1,
            yanchor="top",
            standoff=4,
        )

    fig.update_layout(
        xaxis=dict(
            title="Rating Clásico",
            range=[1380, 2880],
            tickmode="linear",
            dtick=200,
        ),
        yaxis=dict(title="Número de jugadores"),
        bargap=0.02,
    )
    return apply_plotly_theme(fig, height=380, showlegend=False)



@st.cache_data
def fig_bar_titles(titled_df: pd.DataFrame) -> go.Figure:
    """Barras horizontales del desglose de titulados."""
    bar_colors = [TITLE_COLORS.get(l, C_MUTED) for l in titled_df["label"]]
    fig = go.Figure(
        go.Bar(
            x=titled_df["n"],
            y=titled_df["label"],
            orientation="h",
            text=titled_df["n"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            marker_color=bar_colors,
            marker_line_color="rgba(0,0,0,0.15)",
            marker_line_width=0.6,
            hovertemplate="<b>%{y}</b><br>Jugadores: %{x:,}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Número de jugadores"),
        margin=dict(l=10, r=80, t=10, b=10),
    )
    return apply_plotly_theme(fig, height=320, showlegend=False)


@st.cache_data
def fig_heatmap_titles(heat_df: pd.DataFrame) -> go.Figure:
    """Heatmap de concentración de títulos de élite por federación."""
    fig = go.Figure(
        go.Heatmap(
            z=heat_df.values,
            x=["Gran Maestro (GM)", "Maestro Internacional (IM)", "Maestro FIDE (FM)"],
            y=heat_df.index.tolist(),
            colorscale=[
                [0.0, "#F0F4F8"],
                [0.4, "#4A7BB5"],
                [1.0, "#1E3A5F"],
            ],
            text=heat_df.values,
            texttemplate="%{text}",
            textfont=dict(size=12),
            hovertemplate="<b>%{y}</b> — %{x}<br>Jugadores: %{z}<extra></extra>",
            showscale=True,
            colorbar=dict(
                title="Jugadores",
                tickfont=dict(size=10),
                len=0.8,
                thickness=12,
            ),
        )
    )
    fig.update_layout(
        xaxis=dict(side="top", tickfont_size=12),
        yaxis=dict(autorange="reversed", tickfont_size=13),
        margin=dict(l=10, r=20, t=60, b=10),
    )
    return apply_plotly_theme(fig, height=440, showlegend=False)


@st.cache_data
def fig_stacked_gender_federations(fed_sex: pd.DataFrame) -> go.Figure:
    """Barras apiladas horizontales de proporción de género por país."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Femenino",
            x=fed_sex["pct_F"],
            y=fed_sex["country"],
            orientation="h",
            marker_color=C_RED,
            text=fed_sex["pct_F"].apply(lambda v: f"{v:.1f} %"),
            textposition="inside",
            textfont=dict(color="white", size=10),
            hovertemplate="<b>%{y}</b> — Femenino<br>%{x:.1f} %<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Masculino",
            x=fed_sex["pct_M"],
            y=fed_sex["country"],
            orientation="h",
            marker_color=C_NAVY,
            text=fed_sex["pct_M"].apply(lambda v: f"{v:.1f} %"),
            textposition="inside",
            textfont=dict(color="white", size=10),
            hovertemplate="<b>%{y}</b> — Masculino<br>%{x:.1f} %<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="stack",
        xaxis=dict(title="Porcentaje de jugadores", range=[0, 100], ticksuffix=" %"),
    )
    return apply_plotly_theme(fig, height=540)


@st.cache_data
def fig_pyramid_categories(cat_df: pd.DataFrame) -> go.Figure:
    """Pirámide poblacional por categorías FIDE."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Masculino",
            x=-cat_df["M"],
            y=cat_df["categoria"],
            orientation="h",
            marker_color=C_NAVY,
            customdata=cat_df[["M", "pct_M"]].values,
            hovertemplate="<b>%{y}</b> — Masculino<br>Jugadores: %{customdata[0]:,}<br>Proporción: %{customdata[1]:.1f} %<extra></extra>",
            text=cat_df["M"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            textfont=dict(size=10),
        )
    )
    fig.add_trace(
        go.Bar(
            name="Femenino",
            x=cat_df["F"],
            y=cat_df["categoria"],
            orientation="h",
            marker_color=C_RED,
            customdata=cat_df[["F", "pct_F"]].values,
            hovertemplate="<b>%{y}</b> — Femenino<br>Jugadoras: %{customdata[0]:,}<br>Proporción: %{customdata[1]:.1f} %<extra></extra>",
            text=cat_df["F"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            textfont=dict(size=10),
        )
    )

    max_val = int(cat_df["M"].max() * 1.25)
    ticks = list(range(-max_val, max_val + 1, 50_000))
    tick_labels = [f"{abs(t):,}" for t in ticks]

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            title="Número de jugadores (Hombres ◀ | ▶ Mujeres)",
            tickvals=ticks,
            ticktext=tick_labels,
            zeroline=True,
            zerolinecolor="#1C2333",
            zerolinewidth=1.5,
        ),
        yaxis=dict(title="Categoría FIDE", tickfont_size=12),
        bargap=0.15,
        margin=dict(l=10, r=80, t=10, b=10),
    )
    return apply_plotly_theme(fig, height=450)


@st.cache_data
def fig_pyramid_ages(pyramid_age: pd.DataFrame) -> go.Figure:
    """Pirámide poblacional por rangos quinquenales de edad."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Masculino",
            x=-pyramid_age["M"],
            y=pyramid_age["age_bin"],
            orientation="h",
            marker_color=C_NAVY,
            customdata=pyramid_age["M"],
            hovertemplate="<b>%{y}</b> — Masculino<br>Jugadores: %{customdata:,}<extra></extra>",
            text=pyramid_age["M"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            textfont=dict(size=9),
        )
    )
    fig.add_trace(
        go.Bar(
            name="Femenino",
            x=pyramid_age["F"],
            y=pyramid_age["age_bin"],
            orientation="h",
            marker_color=C_RED,
            customdata=pyramid_age["F"],
            hovertemplate="<b>%{y}</b> — Femenino<br>Jugadoras: %{x:,}<extra></extra>",
            text=pyramid_age["F"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            textfont=dict(size=9),
        )
    )

    max_val = int(pyramid_age["M"].max() * 1.25)
    ticks = list(range(-max_val, max_val + 1, 20_000))
    tick_labels = [f"{abs(t):,}" for t in ticks]

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            title="Número de jugadores (Hombres ◀ | ▶ Mujeres)",
            tickvals=ticks,
            ticktext=tick_labels,
            zeroline=True,
            zerolinecolor="#1C2333",
            zerolinewidth=1.5,
        ),
        yaxis=dict(title="Grupo de edad", tickfont_size=11),
        bargap=0.08,
        margin=dict(l=10, r=80, t=10, b=10),
    )
    return apply_plotly_theme(fig, height=580)


@st.cache_data
def fig_line_gender_drop(cat_df: pd.DataFrame, pct_f_global: float) -> go.Figure:
    """Gráfico de línea con la caída de cuota femenina por cohorte."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=cat_df["categoria"],
            y=cat_df["pct_F"],
            mode="lines+markers+text",
            name="% Femenino",
            line=dict(color=C_RED, width=3),
            marker=dict(size=9, color=C_RED),
            text=cat_df["pct_F"].apply(lambda v: f"{v:.1f} %"),
            textposition="top center",
            hovertemplate="<b>%{x}</b><br>Participación femenina: %{y:.1f} %<extra></extra>",
        )
    )
    fig.add_hline(
        y=pct_f_global,
        line_dash="dot",
        line_color=C_MUTED,
        annotation_text=f"Promedio general ({pct_f_global:.1f} %)",
        annotation_position="bottom right",
    )
    fig.update_layout(
        xaxis=dict(title="Categoría FIDE"),
        yaxis=dict(title="Porcentaje femenino (%)", ticksuffix=" %", range=[0, 24]),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    return apply_plotly_theme(fig, height=320, showlegend=False)


@st.cache_data
def fig_parity_federations(best_parity: pd.DataFrame, pct_f_global: float) -> go.Figure:
    """Barras de federaciones con mayor paridad de género."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=best_parity["pct_F"],
            y=best_parity["country"],
            orientation="h",
            marker_color=[
                "#E84855" if v >= 20 else "#F1948A" if v >= 15 else "#FADBD8"
                for v in best_parity["pct_F"]
            ],
            text=best_parity["pct_F"].apply(lambda v: f"{v:.1f} %"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>% Femenino: %{x:.1f} %<extra></extra>",
        )
    )
    fig.add_vline(
        x=pct_f_global,
        line_dash="dash",
        line_color=C_MUTED,
        annotation_text=f"Media mundial<br>{pct_f_global:.1f} %",
        annotation_position="bottom right",
        annotation_font_size=10,
    )
    fig.update_layout(
        xaxis=dict(title="% de jugadoras", ticksuffix=" %", range=[0, 40]),
        margin=dict(l=10, r=60, t=10, b=10),
    )
    return apply_plotly_theme(fig, height=380, showlegend=False)


@st.cache_data
def fig_youth_categories(cat_summary: pd.DataFrame) -> go.Figure:
    """Barras agrupadas de volumen juvenil por sexo."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Femenino",
            x=cat_summary["categoria"],
            y=cat_summary["F"],
            marker_color=C_RED,
            text=cat_summary["F"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            hovertemplate="<b>%{x}</b> — Femenino<br>Jugadoras: %{y:,}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Masculino",
            x=cat_summary["categoria"],
            y=cat_summary["M"],
            marker_color=C_NAVY,
            text=cat_summary["M"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            hovertemplate="<b>%{x}</b> — Masculino<br>Jugadores: %{y:,}<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="group",
        xaxis=dict(title="Categoría FIDE", tickfont_size=12),
        yaxis=dict(title="Número de jugadores"),
        bargap=0.15,
        bargroupgap=0.05,
    )
    return apply_plotly_theme(fig, height=420)


@st.cache_data
def fig_youth_elo_curves(df_elo: pd.DataFrame) -> go.Figure:
    """Evolución de la mediana de Elo por categoría juvenil."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_elo["categoria"],
            y=df_elo["classic_med"],
            mode="lines+markers+text",
            name="Clásico",
            line=dict(color=C_NAVY, width=3),
            marker=dict(size=8, color=C_NAVY),
            text=df_elo["classic_med"].apply(lambda v: f"{int(v)}"),
            textposition="top center",
            hovertemplate="<b>%{x} — Clásico</b><br>Mediana: %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_elo["categoria"],
            y=df_elo["rapid_med"],
            mode="lines+markers+text",
            name="Rápido",
            line=dict(color=C_BLUE, width=2.5, dash="dash"),
            marker=dict(size=7, color=C_BLUE),
            text=df_elo["rapid_med"].apply(lambda v: f"{int(v)}"),
            textposition="bottom center",
            hovertemplate="<b>%{x} — Rápido</b><br>Mediana: %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_elo["categoria"],
            y=df_elo["blitz_med"],
            mode="lines+markers",
            name="Blitz",
            line=dict(color=C_AMBER, width=2, dash="dot"),
            marker=dict(size=6, color=C_AMBER),
            hovertemplate="<b>%{x} — Blitz</b><br>Mediana: %{y:.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Categoría FIDE"),
        yaxis=dict(title="Mediana de Elo", range=[1440, 1760]),
    )
    return apply_plotly_theme(fig, height=380)


@st.cache_data
def fig_youth_elo_bands(df_elo: pd.DataFrame) -> go.Figure:
    """Banda de rendimiento central (IQR) y percentil P99 de élite."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_elo["categoria"],
            y=df_elo["classic_p75"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_elo["categoria"],
            y=df_elo["classic_p25"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(30, 58, 95, 0.15)",
            name="Rango central (P25–P75)",
            hovertemplate="<b>%{x}</b><br>P25: %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_elo["categoria"],
            y=df_elo["classic_med"],
            mode="lines+markers",
            line=dict(color=C_NAVY, width=2.5),
            name="Mediana",
            hovertemplate="<b>%{x}</b><br>Mediana: %{y:.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_elo["categoria"],
            y=df_elo["classic_p99"],
            mode="lines+markers",
            line=dict(color="#C0392B", width=2, dash="dot"),
            name="Élite P99",
            hovertemplate="<b>%{x}</b><br>P99 (Top 1 %): %{y:.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Categoría FIDE"),
        yaxis=dict(title="Rating Clásico"),
    )
    return apply_plotly_theme(fig, height=380)


@st.cache_data
def fig_cantera_pct(top_cantera_pct: pd.DataFrame, pct_youth_global: float) -> go.Figure:
    """Barras horizontales de cuota juvenil por país."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=top_cantera_pct["pct_juvenil"],
            y=top_cantera_pct["country"],
            orientation="h",
            marker_color=C_BLUE,
            text=top_cantera_pct["pct_juvenil"].apply(lambda v: f"{v:.1f} %"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Cuota juvenil: %{x:.1f} %<extra></extra>",
        )
    )
    fig.add_vline(
        x=pct_youth_global,
        line_dash="dash",
        line_color=C_MUTED,
        annotation_text=f"Media mundial ({pct_youth_global:.1f} %)",
        annotation_position="bottom right",
    )
    fig.update_layout(
        xaxis=dict(
            title="% de jugadores en categorías Sub-20",
            range=[0, 100],
            ticksuffix=" %",
        ),
        margin=dict(l=10, r=60, t=10, b=10),
    )
    return apply_plotly_theme(fig, height=400, showlegend=False)


@st.cache_data
def fig_cantera_vol(top_cantera_vol: pd.DataFrame) -> go.Figure:
    """Barras horizontales de volumen absoluto juvenil por país."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=top_cantera_vol["juveniles"],
            y=top_cantera_vol["country"],
            orientation="h",
            marker_color=C_NAVY,
            text=top_cantera_vol["juveniles"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Jugadores juveniles: %{x:,}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Número de jugadores juveniles"),
        margin=dict(l=10, r=60, t=10, b=10),
    )
    return apply_plotly_theme(fig, height=400, showlegend=False)


@st.cache_data
def fig_venezuela_modalities(n_classic: int, n_rapid: int, n_blitz: int, total_ven: int) -> go.Figure:
    """Barras comparativas de ritmos de juego en Venezuela."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Clásico", "Rápido", "Blitz"],
            y=[n_classic, n_rapid, n_blitz],
            marker_color=[C_NAVY, C_BLUE, C_AMBER],
            text=[
                f"{n_classic:,}<br>({n_classic/total_ven*100:.1f} %)",
                f"{n_rapid:,}<br>({n_rapid/total_ven*100:.1f} %)",
                f"{n_blitz:,}<br>({n_blitz/total_ven*100:.1f} %)",
            ],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Jugadores con rating: %{y:,}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Ritmo de juego oficial"),
        yaxis=dict(title="Jugadores con Elo oficial > 0", range=[0, 2600]),
        margin=dict(l=10, r=10, t=20, b=10),
    )
    return apply_plotly_theme(fig, height=360, showlegend=False)


@st.cache_data
def fig_venezuela_hist(r_classic: pd.Series, r_rapid: pd.Series) -> go.Figure:
    """Histograma solapado de Elo Clásico vs Rápido en Venezuela."""
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=r_classic,
            name="Clásico",
            xbins=dict(start=1400, end=2500, size=30),
            marker_color=C_NAVY,
            opacity=0.75,
            hovertemplate="Clásico [%{x}]: %{y} jugadores<extra></extra>",
        )
    )
    fig.add_trace(
        go.Histogram(
            x=r_rapid,
            name="Rápido",
            xbins=dict(start=1400, end=2500, size=30),
            marker_color=C_BLUE,
            opacity=0.6,
            hovertemplate="Rápido [%{x}]: %{y} jugadores<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="overlay",
        xaxis=dict(title="Rating Elo", range=[1380, 2520]),
        yaxis=dict(title="Número de jugadores"),
    )
    return apply_plotly_theme(fig, height=360)


@st.cache_data
def fig_venezuela_titles(df_titles_bar: pd.DataFrame) -> go.Figure:
    """Barras horizontales de títulos oficiales en Venezuela."""
    fig = go.Figure(
        go.Bar(
            x=df_titles_bar["n"],
            y=df_titles_bar["label"],
            orientation="h",
            text=df_titles_bar["n"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            marker_color=[TITLE_COLORS.get(lbl, C_MUTED) for lbl in df_titles_bar["label"]],
            marker_line_color="rgba(0,0,0,0.15)",
            marker_line_width=0.6,
            hovertemplate="<b>%{y}</b><br>Jugadores: %{x:,}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Número de jugadores titulados"),
        margin=dict(l=10, r=60, t=10, b=10),
    )
    return apply_plotly_theme(fig, height=320, showlegend=False)


@st.cache_data
def fig_venezuela_youth(ven_cats: pd.DataFrame) -> go.Figure:
    """Barras agrupadas por categoría formativa en Venezuela."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=ven_cats["categoria"],
            y=ven_cats["M"],
            name="Masculino",
            marker_color=C_NAVY,
            text=ven_cats["M"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            hovertemplate="<b>%{x}</b> — Masculino: %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=ven_cats["categoria"],
            y=ven_cats["F"],
            name="Femenino",
            marker_color=C_RED,
            text=ven_cats["F"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            hovertemplate="<b>%{x}</b> — Femenino: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="group",
        xaxis=dict(title="Categoría formativa"),
        yaxis=dict(title="Número de jugadores"),
    )
    return apply_plotly_theme(fig, height=380)
