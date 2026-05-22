from __future__ import annotations

import altair as alt
import pandas as pd

# iMednet brand palette — used across all charts
PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


def _color_encoding(field: str) -> alt.Color:
    return alt.Color(f"{field}:N", scale=alt.Scale(range=PALETTE))


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    title: str = "",
    x_title: str | None = None,
    y_title: str | None = None,
) -> alt.Chart:
    """Returns an Altair horizontal bar chart."""
    chart = alt.Chart(df).mark_bar()
    if color:
        chart = chart.encode(
            x=alt.X(f"{x}:Q", title=x_title),
            y=alt.Y(f"{y}:N", title=y_title, sort="-x"),
            color=_color_encoding(color),
            tooltip=[alt.Tooltip(f"{y}:N"), alt.Tooltip(f"{x}:Q"), alt.Tooltip(f"{color}:N")],
        )
    else:
        chart = chart.encode(
            x=alt.X(f"{x}:Q", title=x_title),
            y=alt.Y(f"{y}:N", title=y_title, sort="-x"),
            color=alt.value(PALETTE[0]),
            tooltip=[alt.Tooltip(f"{y}:N"), alt.Tooltip(f"{x}:Q")],
        )

    return chart.properties(width="container", title=title)


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    title: str = "",
) -> alt.Chart:
    """Returns an Altair temporal line chart with tooltip."""
    chart = alt.Chart(df).mark_line(point=True)
    if color:
        chart = chart.encode(
            x=alt.X(f"{x}:T"),
            y=alt.Y(f"{y}:Q"),
            color=_color_encoding(color),
            tooltip=[alt.Tooltip(f"{x}:T"), alt.Tooltip(f"{y}:Q"), alt.Tooltip(f"{color}:N")],
        )
    else:
        chart = chart.encode(
            x=alt.X(f"{x}:T"),
            y=alt.Y(f"{y}:Q"),
            color=alt.value(PALETTE[0]),
            tooltip=[alt.Tooltip(f"{x}:T"), alt.Tooltip(f"{y}:Q")],
        )

    return chart.properties(width="container", title=title)


def pie_chart(
    df: pd.DataFrame,
    theta: str,
    color: str,
    title: str = "",
) -> alt.Chart:
    """Returns an Altair arc/pie chart."""
    return (
        alt.Chart(df)
        .mark_arc()
        .encode(
            theta=alt.Theta(f"{theta}:Q"),
            color=_color_encoding(color),
            tooltip=[alt.Tooltip(f"{color}:N"), alt.Tooltip(f"{theta}:Q")],
        )
        .properties(width="container", title=title)
    )
