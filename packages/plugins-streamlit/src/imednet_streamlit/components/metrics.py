from __future__ import annotations

import streamlit as st


def kpi_card(
    label: str,
    value: int | float | str,
    delta: str | None = None,
    help: str | None = None,
) -> None:
    """Renders a single KPI metric card using st.metric."""
    st.metric(label=label, value=value, delta=delta, help=help)


def kpi_row(metrics: list[dict]) -> None:
    """
    Renders a horizontal row of KPI cards.

    :param metrics:
        List of dicts with keys: label, value, delta (optional), help (optional)

    Example::

        kpi_row([
            {"label": "Open Queries", "value": 42},
            {"label": "Subjects Enrolled", "value": 120, "delta": "+5 this week"},
        ])
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            kpi_card(
                label=metric["label"],
                value=metric["value"],
                delta=metric.get("delta"),
                help=metric.get("help"),
            )
