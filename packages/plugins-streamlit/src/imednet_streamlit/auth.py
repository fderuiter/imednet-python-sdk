"""TODO: Add docstring."""

from __future__ import annotations

import streamlit as st

from imednet import ImednetSDK
from imednet.spi.facade import ImednetFacade

_KEY_API_KEY = "_imednet_api_key"
_KEY_SECURITY_KEY = "_imednet_security_key"
_KEY_STUDY_KEY = "_imednet_study_key"
_KEY_SDK = "_imednet_sdk"
_KEY_CONNECTED = "_imednet_connected"

__all__ = ["render_auth_sidebar", "get_sdk", "get_study_key", "clear_credentials"]


def _build_sdk(api_key: str, security_key: str) -> None:
    """Construct and cache an authenticated SDK instance."""
    st.session_state[_KEY_SDK] = ImednetSDK(
        api_key=api_key,
        security_key=security_key,
    )


def _mark_disconnected() -> None:
    """TODO: Add docstring."""
    st.session_state[_KEY_CONNECTED] = False
    st.session_state.pop(_KEY_SDK, None)


import os
import sqlite3


def get_tenant_credentials(study_key: str) -> tuple[str | None, str | None]:
    """TODO: Add docstring."""
    db_path = os.environ.get(
        "IMEDNET_TENANT_DB_PATH", os.path.expanduser("~/.imednet/enterprise_portal.sqlite3")
    )
    if not os.path.exists(db_path):
        return None, None
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT api_key, security_key FROM tenants WHERE study_key=?", (study_key,)
            ).fetchone()
            if row:
                return row[0], row[1]
    except Exception:
        pass
    return None, None


def get_provisioned_studies() -> list[str]:
    """TODO: Add docstring."""
    db_path = os.environ.get(
        "IMEDNET_TENANT_DB_PATH", os.path.expanduser("~/.imednet/enterprise_portal.sqlite3")
    )
    if not os.path.exists(db_path):
        return []
    try:
        with sqlite3.connect(db_path) as conn:
            return [row[0] for row in conn.execute("SELECT study_key FROM tenants")]
    except sqlite3.OperationalError:
        return []


def render_auth_sidebar() -> bool:
    """Render sidebar authentication controls and update session auth state.

    Returns:
        ``True`` when a valid SDK connection is active in ``st.session_state``;
        otherwise ``False``.
    """
    with st.sidebar:
        st.header("🔐 Enterprise SSO")

        # OIDC integration for corporate credentials
        is_logged_in = getattr(st.user, "is_logged_in", False) or "email" in getattr(st, "user", {})

        if not is_logged_in:
            st.info("Please authenticate using your corporate IdP.")
            if hasattr(st, "login"):
                if st.button("Login via SSO"):
                    st.login()
            else:
                st.warning("SSO module not found in this Streamlit version.")
            return False

        user_email = getattr(st.user, "email", "Corporate User")
        if not user_email and hasattr(st.user, "get"):
            user_email = st.user.get("email", "Corporate User")

        st.success(f"SSO Active: {user_email}")

        studies = get_provisioned_studies()
        if not studies:
            st.warning("No studies available. Contact Global Admin to provision environments.")
            return False

        study_key = st.selectbox("Select Authorized Study", options=studies, key=_KEY_STUDY_KEY)

        if st.button("Connect"):
            api_key, security_key = get_tenant_credentials(study_key)
            if not api_key or not security_key:
                st.error("Managed credentials for this tenant are missing.")
            else:
                try:
                    _build_sdk(api_key=api_key, security_key=security_key)
                    st.session_state[_KEY_CONNECTED] = True
                    st.success("Connected ✓")
                except Exception as exc:
                    _mark_disconnected()
                    err_str = str(exc)
                    if "Unauthorized" in err_str or "AuthError" in type(exc).__name__:
                        st.warning("Session expired or Unauthorized. Redirecting to SSO flow...")
                        if hasattr(st, "login"):
                            st.login()
                    else:
                        st.error(f"Connection failed ({type(exc).__name__}).")

    return bool(st.session_state.get(_KEY_CONNECTED))


def get_sdk() -> ImednetFacade:
    """Return the authenticated SDK from session state.

    Returns:
        The connected :class:`imednet.spi.facade.ImednetFacade` instance.

    Raises:
        RuntimeError: If the user is not connected or no SDK is stored.
    """
    sdk = st.session_state.get(_KEY_SDK)
    if not st.session_state.get(_KEY_CONNECTED) or sdk is None:
        raise RuntimeError(
            "SDK is not connected. Ensure credentials are entered and Connect is clicked."
        )
    return sdk


def get_study_key() -> str:
    """Return the selected study key from session state.

    Returns:
        The selected study key string.

    Raises:
        RuntimeError: If no study key is present in session state.
    """
    study_key = st.session_state.get(_KEY_STUDY_KEY)
    if not isinstance(study_key, str) or not study_key:
        raise RuntimeError("Study key is not set. Call render_auth_sidebar() first.")
    return study_key


def clear_credentials() -> None:
    """Remove all authentication state from Streamlit session storage.

    This removes the cached SDK instance, connection flag, and any credential
    input values currently held in ``st.session_state``.
    """
    for key in (_KEY_API_KEY, _KEY_SECURITY_KEY, _KEY_STUDY_KEY, _KEY_SDK, _KEY_CONNECTED):
        st.session_state.pop(key, None)
