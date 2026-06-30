"""Unit tests for components tables."""

from __future__ import annotations

import pandas as pd
import pytest

from imednet_streamlit.components import filterable_dataframe, paginated_grid, tables


class _FakeColumn:
    """Test suite for  FakeColumn."""

    def button(self, *_: object, **__: object) -> bool:
        """Helper function to button."""
        return False

    def caption(self, *_: object, **__: object) -> None:
        """Helper function to caption."""
        return None


class _FakeTableStreamlit:
    """Test suite for  FakeTableStreamlit."""

    def __init__(self, *, query: str) -> None:
        """Initialize the test object."""
        self._query = query
        self.dataframe_calls: list[pd.DataFrame] = []
        self.text_input_keys: list[str] = []
        self.session_state: dict[str, object] = {}

    def text_input(self, _: str, *, key: str) -> str:
        """Helper function to text input."""
        self.text_input_keys.append(key)
        return self._query

    def selectbox(self, _: str, *, options: tuple[object, ...], key: str, index: int = 0) -> int:
        """Helper function to selectbox."""
        self.session_state[key] = options[index]
        return int(options[index])

    def columns(self, _: list[int]) -> tuple[_FakeColumn, _FakeColumn, _FakeColumn]:
        """Helper function to columns."""
        return (_FakeColumn(), _FakeColumn(), _FakeColumn())

    def dataframe(self, df: pd.DataFrame, *, use_container_width: bool, height: int) -> None:
        """Helper function to dataframe."""
        assert use_container_width is True
        assert height == 400
        self.dataframe_calls.append(df.copy())


def test_filterable_dataframe_applies_case_insensitive_row_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that filterable dataframe applies case insensitive row filter."""
    fake_st = _FakeTableStreamlit(query="site b")
    monkeypatch.setattr(tables, "st", fake_st)
    monkeypatch.setattr(paginated_grid, "st", fake_st)
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
    """Test that filterable dataframe empty query returns original."""
    fake_st = _FakeTableStreamlit(query="")
    monkeypatch.setattr(tables, "st", fake_st)
    monkeypatch.setattr(paginated_grid, "st", fake_st)
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
