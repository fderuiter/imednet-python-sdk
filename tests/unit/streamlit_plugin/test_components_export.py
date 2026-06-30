"""Unit tests for components export."""

from __future__ import annotations

import io

import pandas as pd
import pytest

import imednet_streamlit.components.export as export_components
from imednet_streamlit.components import csv_download_button, excel_download_button


class _FakeExportStreamlit:
    """Test suite for  FakeExportStreamlit."""

    def __init__(self) -> None:
        """Initialize the test object."""
        self.download_calls: list[dict[str, object]] = []

    def download_button(
        self,
        *,
        label: str,
        data: bytes,
        file_name: str,
        mime: str,
    ) -> None:
        """Helper function to download button."""
        self.download_calls.append(
            {"label": label, "data": data, "file_name": file_name, "mime": mime}
        )


def test_csv_download_button_exports_utf8_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that csv download button exports utf8 csv."""
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
    assert data.decode("utf-8").startswith("name,count\r\nJosé,1\r\n") or data.decode(
        "utf-8"
    ).startswith("name,count\nJosé,1\n")


def test_excel_download_button_exports_valid_xlsx(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that excel download button exports valid xlsx."""
    fake_st = _FakeExportStreamlit()
    monkeypatch.setattr(export_components, "st", fake_st)
    df = pd.DataFrame({"name": ["Site A"], "count": [3]})

    excel_download_button(df, filename="report.xlsx")

    assert len(fake_st.download_calls) == 1
    call = fake_st.download_calls[0]
    assert call["file_name"] == "report.xlsx"
    assert call["mime"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    data = call["data"]
    assert isinstance(data, bytes)
    exported = pd.read_excel(io.BytesIO(data))
    assert exported.to_dict(orient="list") == {"name": ["Site A"], "count": [3]}
