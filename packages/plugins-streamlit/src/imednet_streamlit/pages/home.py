"""Home page for the iMednet EDC Dashboard.

Provides a high-level overview of the connected study and quick access to
common dashboard modules.
"""

from __future__ import annotations

import streamlit as st

from imednet_streamlit.auth import get_sdk, get_study_key

st.title("🏥 iMednet EDC Dashboard")

if not st.session_state.get("_imednet_connected"):
    st.info("Please authenticate using the sidebar to access the dashboard.")
    st.markdown("""
    **Getting Started:**
    1. Enter your **API Key** and **Security Key** in the sidebar
    2. Enter the **Study Key** for the study you want to report on
    3. Click **Connect**
    """)
else:
    study_key = get_study_key()
    get_sdk()
    st.success(f"Connected to study: `{study_key}`")
    st.markdown("Use the sidebar navigation to explore reports.")
