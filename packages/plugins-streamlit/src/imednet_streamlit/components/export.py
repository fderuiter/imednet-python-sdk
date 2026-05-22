from __future__ import annotations

import io

import pandas as pd
import streamlit as st


def csv_download_button(df: pd.DataFrame, filename: str, label: str = "⬇ Download CSV") -> None:
    """Renders a download button that exports the DataFrame as CSV."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label=label, data=csv, file_name=filename, mime="text/csv")


def excel_download_button(df: pd.DataFrame, filename: str, label: str = "⬇ Download Excel") -> None:
    """Renders a download button that exports the DataFrame as Excel."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    st.download_button(
        label=label,
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
