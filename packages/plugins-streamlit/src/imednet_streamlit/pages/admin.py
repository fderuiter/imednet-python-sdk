"""Enterprise administration portal.

Provides high-level management for tenants, study provisioning, and
cross-study system health monitoring.
"""

from __future__ import annotations

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
            from imednet_streamlit.auth import get_db_path
            from imednet_streamlit.credentials import CredentialRepository

            db_path = get_db_path()
            repo = CredentialRepository(db_path)
            repo.provision_tenant(
                study_key=study_key.strip(),
                api_key=api_key.strip(),
                security_key=security_key.strip(),
                env_url=env_url.strip() if env_url.strip() else None,
            )
            st.success(
                f"Tenant environment for `{study_key}` automatically provisioned in managed database!"
            )
        except Exception as e:
            st.error(f"Failed to provision study: {e}")
