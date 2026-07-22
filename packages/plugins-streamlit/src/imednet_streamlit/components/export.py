"""Data export components for Streamlit.

Provides standardized buttons for downloading DataFrames as CSV or Excel
files.
"""

from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from imednet.spi.utils import sanitize_csv_formula


def csv_download_button(df: pd.DataFrame, filename: str, label: str = "⬇ Download CSV") -> None:
    """Render a CSV download button for a DataFrame.

    Args:
        df: DataFrame to serialize.
        filename: Output filename displayed in the browser download prompt.
        label: Button label text.
    """
    safe_df = (
        df.map(sanitize_csv_formula) if hasattr(df, "map") else df.applymap(sanitize_csv_formula)  # type: ignore[operator, unused-ignore]
    )
    csv = safe_df.to_csv(index=False).encode("utf-8")
    st.download_button(label=label, data=csv, file_name=filename, mime="text/csv")


def excel_download_button(df: pd.DataFrame, filename: str, label: str = "⬇ Download Excel") -> None:
    """Render an Excel download button for a DataFrame.

    Args:
        df: DataFrame to serialize.
        filename: Output filename displayed in the browser download prompt.
        label: Button label text.
    """
    buffer = io.BytesIO()
    safe_df = (
        df.map(sanitize_csv_formula) if hasattr(df, "map") else df.applymap(sanitize_csv_formula)  # type: ignore[operator, unused-ignore]
    )
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        safe_df.to_excel(writer, index=False)
    st.download_button(
        label=label,
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
