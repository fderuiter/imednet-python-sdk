"""TODO: Add docstring."""

from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

import imednet_streamlit.components.paginated_grid as paginated_grid
from imednet_streamlit.components.paginated_grid import top_n_with_other


class _FakeColumn:
    """TODO: Add docstring."""

    def __init__(self, *, next_click: bool = False, prev_click: bool = False) -> None:
        """TODO: Add docstring."""
        self._next_click = next_click
        self._prev_click = prev_click
        self.captions: list[str] = []

    def button(self, label: str, **kwargs: Any) -> bool:
        """TODO: Add docstring."""
        if label == "Next":
            return self._next_click
        if label == "Previous":
            return self._prev_click
        return False

    def caption(self, value: str) -> None:
        """TODO: Add docstring."""
        self.captions.append(value)


def test_top_n_with_other_adds_remainder_bucket() -> None:
    """TODO: Add docstring."""
    df = pd.DataFrame(
        {
            "label": ["A", "B", "C", "D"],
            "count": [10, 8, 3, 2],
        }
    )

    result = top_n_with_other(df, label_column="label", value_column="count", top_n=2)

    assert result["label"].tolist() == ["A", "B", "Other"]
    assert result["count"].tolist() == [10, 8, 5]


def test_top_n_with_other_empty_dataframe_returns_empty() -> None:
    """TODO: Add docstring."""
    df = pd.DataFrame({"label": [], "count": []})

    result = top_n_with_other(df, label_column="label", value_column="count")

    assert result.empty


def test_top_n_with_other_all_rows_fit_in_top_n_returns_no_other() -> None:
    """TODO: Add docstring."""
    df = pd.DataFrame({"label": ["A", "B"], "count": [5, 3]})

    result = top_n_with_other(df, label_column="label", value_column="count", top_n=10)

    assert "Other" not in result["label"].tolist()
    assert len(result) == 2


def test_top_n_with_other_zero_remainder_omits_other_row() -> None:
    """TODO: Add docstring."""
    df = pd.DataFrame({"label": ["A", "B", "C"], "count": [5, 3, 0]})

    result = top_n_with_other(df, label_column="label", value_column="count", top_n=2)

    assert "Other" not in result["label"].tolist()
    assert len(result) == 2


def test_paginated_slice_limits_rows_to_active_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TODO: Add docstring."""
    session_state: dict[str, Any] = {}
    prev_col = _FakeColumn()
    info_col = _FakeColumn()
    next_col = _FakeColumn()

    monkeypatch.setattr(
        paginated_grid.st, "session_state", session_state, raising=False
    )
    monkeypatch.setattr(paginated_grid.st, "selectbox", lambda *args, **kwargs: 100)
    monkeypatch.setattr(
        paginated_grid.st, "columns", lambda spec: [prev_col, info_col, next_col]
    )

    df = pd.DataFrame({"row": range(20_000)})
    page_df = paginated_grid.paginated_slice(df, key="grid")

    assert len(page_df) == 100
    assert page_df["row"].iloc[0] == 0
    assert page_df["row"].iloc[-1] == 99
    assert "Showing 1-100 of 20000" in info_col.captions[0]


def test_paginated_slice_prev_button_decrements_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TODO: Add docstring."""
    session_state: dict[str, Any] = {"grid_page": 3}
    prev_col = _FakeColumn(prev_click=True)
    info_col = _FakeColumn()
    next_col = _FakeColumn()

    monkeypatch.setattr(
        paginated_grid.st, "session_state", session_state, raising=False
    )
    monkeypatch.setattr(paginated_grid.st, "selectbox", lambda *args, **kwargs: 100)
    monkeypatch.setattr(
        paginated_grid.st, "columns", lambda spec: [prev_col, info_col, next_col]
    )

    df = pd.DataFrame({"row": range(500)})
    page_df = paginated_grid.paginated_slice(df, key="grid")

    assert session_state["grid_page"] == 2
    assert page_df["row"].iloc[0] == 100
    assert page_df["row"].iloc[-1] == 199


def test_paginated_slice_clamps_page_above_total_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TODO: Add docstring."""
    session_state: dict[str, Any] = {"grid_page": 999}
    prev_col = _FakeColumn()
    info_col = _FakeColumn()
    next_col = _FakeColumn()

    monkeypatch.setattr(
        paginated_grid.st, "session_state", session_state, raising=False
    )
    monkeypatch.setattr(paginated_grid.st, "selectbox", lambda *args, **kwargs: 100)
    monkeypatch.setattr(
        paginated_grid.st, "columns", lambda spec: [prev_col, info_col, next_col]
    )

    df = pd.DataFrame({"row": range(150)})
    page_df = paginated_grid.paginated_slice(df, key="grid")

    assert session_state["grid_page"] == 2
    assert len(page_df) == 50


def test_paginated_slice_custom_page_size_not_in_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TODO: Add docstring."""
    session_state: dict[str, Any] = {}
    prev_col = _FakeColumn()
    info_col = _FakeColumn()
    next_col = _FakeColumn()

    monkeypatch.setattr(
        paginated_grid.st, "session_state", session_state, raising=False
    )
    monkeypatch.setattr(paginated_grid.st, "selectbox", lambda *args, **kwargs: 75)
    monkeypatch.setattr(
        paginated_grid.st, "columns", lambda spec: [prev_col, info_col, next_col]
    )

    df = pd.DataFrame({"row": range(300)})
    page_df = paginated_grid.paginated_slice(
        df, key="grid", page_size_options=(50, 100, 200), default_page_size=75
    )

    assert len(page_df) == 75
