"""Unit tests for components metrics."""

from __future__ import annotations

import pytest

from imednet_streamlit.components import kpi_card, kpi_row, metrics


class _ColumnContext:
    """Test suite for  ColumnContext."""

    def __enter__(self) -> None:
        """Helper function to   enter  ."""
        return None

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Helper function to   exit  ."""
        return None


class _FakeMetricStreamlit:
    """Test suite for  FakeMetricStreamlit."""

    def __init__(self) -> None:
        """Initialize the test object."""
        self.columns_calls: list[int] = []
        self.metrics: list[dict[str, object]] = []

    def columns(self, count: int) -> list[_ColumnContext]:
        """Helper function to columns."""
        self.columns_calls.append(count)
        return [_ColumnContext() for _ in range(count)]

    def metric(
        self,
        *,
        label: str,
        value: int | float | str,
        delta: str | None = None,
        help: str | None = None,
    ) -> None:
        """Helper function to metric."""
        self.metrics.append(
            {
                "label": label,
                "value": value,
                "delta": delta,
                "help": help,
            }
        )


def test_kpi_row_uses_column_count_and_renders_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that kpi row uses column count and renders metrics."""
    fake_st = _FakeMetricStreamlit()
    monkeypatch.setattr(metrics, "st", fake_st)

    kpi_row(
        [
            {"label": "Open Queries", "value": 42},
            {"label": "Subjects Enrolled", "value": 120, "delta": "+5 this week"},
        ]
    )

    assert fake_st.columns_calls == [2]
    assert [metric_call["label"] for metric_call in fake_st.metrics] == [
        "Open Queries",
        "Subjects Enrolled",
    ]


def test_kpi_card_calls_streamlit_metric(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that kpi card calls streamlit metric."""
    fake_st = _FakeMetricStreamlit()
    monkeypatch.setattr(metrics, "st", fake_st)

    kpi_card(label="Subjects", value=120, delta="+5", help="Weekly enrollment")

    assert fake_st.metrics == [
        {
            "label": "Subjects",
            "value": 120,
            "delta": "+5",
            "help": "Weekly enrollment",
        }
    ]
