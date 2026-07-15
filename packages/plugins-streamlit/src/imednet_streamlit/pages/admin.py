"""Enterprise administration portal.

Provides high-level management for tenants, study provisioning, and
cross-study system health monitoring.
"""

from __future__ import annotations

import os
import sqlite3

import streamlit as st

st.title("🏢 Enterprise Admin Portal")
st.markdown("Automated provisioning and multi-tenant study management.")

study_key = st.text_input("New Study Key")
api_key = st.text_input("API Key", type="password")
security_key = st.text_input("Security Key", type="password")
env_url = st.text_input("Environment URL (Optional)")

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
                # Check for env_url column dynamically
                cursor = conn.execute("PRAGMA table_info(tenants)")
                columns = [row[1] for row in cursor.fetchall()]
                if "env_url" not in columns:
                    conn.execute("ALTER TABLE tenants ADD COLUMN env_url TEXT")

                conn.execute(
                    "INSERT OR REPLACE INTO tenants (study_key, api_key, security_key, env_url) VALUES (?, ?, ?, ?)",
                    (
                        study_key.strip(),
                        api_key.strip(),
                        security_key.strip(),
                        env_url.strip() if env_url.strip() else None,
                    ),
                )
            st.success(
                f"Tenant environment for `{study_key}` automatically provisioned in managed database!"
            )
        except Exception as e:
            st.error(f"Failed to provision study: {e}")
