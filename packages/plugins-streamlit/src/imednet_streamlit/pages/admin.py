"""TODO: Add docstring."""
from __future__ import annotations

import os
import sqlite3

import streamlit as st

st.title("🏢 Enterprise Admin Portal")
st.markdown("Automated provisioning and multi-tenant study management.")

study_key = st.text_input("New Study Key")
api_key = st.text_input("API Key", type="password")
security_key = st.text_input("Security Key", type="password")

if st.button("Provision Tenant Environment"):
    if not study_key or not api_key or not security_key:
        st.error("All fields are required to provision a new study.")
    else:
        try:
            db_path = os.environ.get(
                "IMEDNET_TENANT_DB_PATH", os.path.expanduser("~/.imednet/enterprise_portal.sqlite3")
            )
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS tenants (study_key TEXT PRIMARY KEY, api_key TEXT, security_key TEXT)"
                )
                conn.execute(
                    "INSERT OR REPLACE INTO tenants VALUES (?, ?, ?)",
                    (study_key.strip(), api_key.strip(), security_key.strip()),
                )
            st.success(
                f"Tenant environment for `{study_key}` automatically provisioned in managed database!"
            )
        except Exception as e:
            st.error(f"Failed to provision study: {e}")
