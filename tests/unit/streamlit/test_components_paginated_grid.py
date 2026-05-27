from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

import imednet_streamlit.components.paginated_grid as paginated_grid


class _FakeColumn:
    def __init__(self, *, next_click: bool = False, prev_click: bool = False) -> None:
        self._next_click = next_click
        self._prev_click = prev_click
        self.captions: list[str] = []

    def button(self, label: str, **kwargs: Any) -> bool:
        if label == "Next":
            return self._next_click
        if label == "Previous":
            return self._prev_click
        return False

    def caption(self, value: str) -> None:
        self.captions.append(value)


def test_paginated_slice_limits_rows_to_active_page(monkeypatch: pytest.MonkeyPatch) -> None:
    session_state: dict[str, Any] = {}
    prev_col = _FakeColumn()
    info_col = _FakeColumn()
    next_col = _FakeColumn()

    monkeypatch.setattr(paginated_grid.st, "session_state", session_state, raising=False)
    monkeypatch.setattr(paginated_grid.st, "selectbox", lambda *args, **kwargs: 100)
    monkeypatch.setattr(
        paginated_grid.st,
        "columns",
        lambda spec: [prev_col, info_col, next_col],
    )

    df = pd.DataFrame({"row": range(20_000)})
    page_df = paginated_grid.paginated_slice(df, key="records")

    assert len(page_df) == 100
    assert page_df["row"].iloc[0] == 0
    assert page_df["row"].iloc[-1] == 99
    assert "Showing 1-100 of 20000" in info_col.captions[0]


def test_paginated_slice_moves_to_next_page(monkeypatch: pytest.MonkeyPatch) -> None:
    session_state: dict[str, Any] = {"records_page": 1}
    prev_col = _FakeColumn()
    info_col = _FakeColumn()
    next_col = _FakeColumn(next_click=True)

    monkeypatch.setattr(paginated_grid.st, "session_state", session_state, raising=False)
    monkeypatch.setattr(paginated_grid.st, "selectbox", lambda *args, **kwargs: 100)
    monkeypatch.setattr(
        paginated_grid.st,
        "columns",
        lambda spec: [prev_col, info_col, next_col],
    )

    df = pd.DataFrame({"row": range(20_000)})
    page_df = paginated_grid.paginated_slice(df, key="records")

    assert session_state["records_page"] == 2
    assert page_df["row"].iloc[0] == 100
    assert page_df["row"].iloc[-1] == 199
    assert "Page 2 of 200" in info_col.captions[0]


def test_top_n_with_other_adds_remainder_bucket() -> None:
    df = pd.DataFrame({"label": ["A", "B", "C", "D"], "count": [10, 8, 3, 2]})

    result = paginated_grid.top_n_with_other(
        df, label_column="label", value_column="count", top_n=2
    )

    assert result["label"].tolist() == ["A", "B", "Other"]
    assert result["count"].tolist() == [10, 8, 5]
