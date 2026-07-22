"""KPI and metric display components for Streamlit.

Provides card-based layouts for displaying key performance indicators and
high-level study statistics.
"""

from __future__ import annotations

import streamlit as st

from typing import TypedDict
try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired





class MetricConfig(TypedDict):
    label: str
    value: int | float | str
    delta: NotRequired[str | None]
    help: NotRequired[str | None]

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


def kpi_row(metrics: list[MetricConfig]) -> None:
    """Render a horizontal row of KPI metric cards.

    Args:
        metrics: Sequence of metric dictionaries with ``label`` and ``value`` keys.
            Optional keys are ``delta`` and ``help``.
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):  # noqa: B905
        with col:
            kpi_card(
                label=metric["label"],
                value=metric["value"],
                delta=metric.get("delta"),
                help=metric.get("help"),
            )
