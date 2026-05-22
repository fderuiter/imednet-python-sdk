from __future__ import annotations

import pandas as pd
import pytest

from imednet_streamlit.components import filterable_dataframe, tables


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


def test_filterable_dataframe_empty_query_returns_original(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_st = _FakeTableStreamlit(query="")
    monkeypatch.setattr(tables, "st", fake_st)
    df = pd.DataFrame(
        {
            "site": ["Site A", "Site B", "Site C"],
            "count": [5, 9, 2],
        }
    )

    filterable_dataframe(df, key="queries")

    filtered = fake_st.dataframe_calls[0]
    assert len(filtered) == 3
    assert filtered["site"].tolist() == ["Site A", "Site B", "Site C"]
