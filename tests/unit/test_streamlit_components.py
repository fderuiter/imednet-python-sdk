from __future__ import annotations

import altair as alt
import pandas as pd
import pytest

import imednet_streamlit.components.export as export_components
from imednet_streamlit.components import (
    bar_chart,
    csv_download_button,
    filterable_dataframe,
    kpi_row,
    metrics,
    tables,
)


class _ColumnContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None


class _FakeMetricStreamlit:
    def __init__(self) -> None:
        self.columns_calls: list[int] = []
        self.metrics: list[dict[str, object]] = []

    def columns(self, count: int) -> list[_ColumnContext]:
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
        self.metrics.append(
            {
                "label": label,
                "value": value,
                "delta": delta,
                "help": help,
            }
        )


class _FakeTableStreamlit:
    def __init__(self, *, query: str) -> None:
        self._query = query
        self.dataframe_calls: list[pd.DataFrame] = []
        self.text_input_keys: list[str] = []

    def text_input(self, _: str, *, key: str) -> str:
        self.text_input_keys.append(key)
        return self._query

    def dataframe(self, df: pd.DataFrame, *, use_container_width: bool, height: int) -> None:
        assert use_container_width is True
        assert height == 400
        self.dataframe_calls.append(df.copy())


class _FakeExportStreamlit:
    def __init__(self) -> None:
        self.download_calls: list[dict[str, object]] = []

    def download_button(
        self,
        *,
        label: str,
        data: bytes,
        file_name: str,
        mime: str,
    ) -> None:
        self.download_calls.append(
            {"label": label, "data": data, "file_name": file_name, "mime": mime}
        )


def test_kpi_row_uses_column_count_and_renders_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_filterable_dataframe_applies_case_insensitive_row_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_st = _FakeTableStreamlit(query="site b")
    monkeypatch.setattr(tables, "st", fake_st)
    df = pd.DataFrame(
        {
            "site": ["Site A", "Site B", "Site C"],
            "count": [5, 9, 2],
        }
    )

    filterable_dataframe(df, key="queries")

    assert fake_st.text_input_keys == ["filter_queries"]
    filtered = fake_st.dataframe_calls[0]
    assert filtered["site"].tolist() == ["Site B"]
    assert filtered["count"].tolist() == [9]


def test_csv_download_button_exports_utf8_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_st = _FakeExportStreamlit()
    monkeypatch.setattr(export_components, "st", fake_st)
    df = pd.DataFrame({"name": ["José"], "count": [1]})

    csv_download_button(df, filename="report.csv")

    assert len(fake_st.download_calls) == 1
    call = fake_st.download_calls[0]
    assert call["file_name"] == "report.csv"
    assert call["mime"] == "text/csv"
    data = call["data"]
    assert isinstance(data, bytes)
    assert data.decode("utf-8").startswith("name,count\nJosé,1\n")


def test_bar_chart_returns_altair_chart() -> None:
    df = pd.DataFrame({"category": ["A", "B"], "value": [1, 2]})
    chart = bar_chart(df, x="value", y="category", title="Example")

    assert isinstance(chart, alt.Chart)
