"""Metrics module."""

from __future__ import annotations

import streamlit as st


def kpi_card(
    label: str,
    value: int | float | str,
    delta: str | None = None,
    help: str | None = None,
) -> None:
    """Render a single KPI metric card.

    Args:
        label: Metric label displayed above the value.
        value: Metric value displayed in the card.
        delta: Optional delta text (for trend direction).
        help: Optional tooltip/help text.
    """
    st.metric(label=label, value=value, delta=delta, help=help)


def kpi_row(metrics: list[dict]) -> None:
    """Render a horizontal row of KPI metric cards.

    Args:
        metrics: Sequence of metric dictionaries with ``label`` and ``value`` keys.
            Optional keys are ``delta`` and ``help``.
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
