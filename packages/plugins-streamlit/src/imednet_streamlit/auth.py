# pylint: disable=duplicate-code
"""Authentication and multi-tenant session management for Streamlit.

This module provides integration with corporate SSO, study-based credential
discovery from an enterprise tenant database, and SDK lifecycle management
within the Streamlit session state.
"""

from __future__ import annotations

import streamlit as st

from imednet import ImednetSDK
from imednet.spi.facade import ImednetFacade

_KEY_API_KEY = "_imednet_api_key"
_KEY_SECURITY_KEY = "_imednet_security_key"
_KEY_STUDY_KEY = "_imednet_study_key"
_KEY_SDK = "_imednet_sdk"
_KEY_CONNECTED = "_imednet_connected"
_KEY_ENV = "_imednet_env"

__all__ = [
    "clear_credentials",
    "get_db_path",
    "get_sdk",
    "get_study_key",
    "render_auth_sidebar",
]


def _build_sdk(api_key: str, security_key: str, env_url: str | None = None) -> None:
    """Construct and cache an authenticated SDK instance."""
    if env_url:
        st.session_state[_KEY_SDK] = ImednetSDK(
            api_key=api_key,
            security_key=security_key,
            base_url=env_url,
        )
    else:
        st.session_state[_KEY_SDK] = ImednetSDK(
            api_key=api_key,
            security_key=security_key,
        )


def _mark_disconnected() -> None:
    """Mark the session as disconnected and clear the cached SDK.

    This ensures that any subsequent interaction requires a fresh connection,
    and prevents stale SDK instances from being used after a context switch.
    """
    st.session_state[_KEY_CONNECTED] = False
    st.session_state.pop(_KEY_SDK, None)
    # Also clear cache to prevent stale data leaks across contexts
    st.cache_data.clear()


import os

from .credentials import CredentialRepository


def get_db_path() -> str:
    """Resolve the database file path based on the selected environment."""
    base_path = os.environ.get(
        "IMEDNET_TENANT_DB_PATH",
        os.path.expanduser("~/.imednet/enterprise_portal.sqlite3"),
    )

    env = st.session_state.get(_KEY_ENV, "Default")
    if env != "Default":
        dir_name = os.path.dirname(base_path)
        base_name = os.path.basename(base_path)
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}_{env.lower()}{ext}"
        resolved_path = os.path.join(dir_name, new_name)
    else:
        resolved_path = base_path

    # DB initialization logic has been moved to CredentialRepository
    return resolved_path


def get_tenant_credentials(study_key: str) -> tuple[str | None, str | None, str | None]:
    """Fetch API and Security keys and environment URL for a specific study from the tenant database.

    Args:
        study_key: The study identifier.

    Returns:
        A tuple of (api_key, security_key, env_url), or (None, None, None) if not found.
    """
    db_path = get_db_path()
    repo = CredentialRepository(db_path)
    return repo.get_credentials(study_key)


def get_provisioned_studies() -> list[str]:
    """Return a list of all study keys available in the tenant database."""
    db_path = get_db_path()
    repo = CredentialRepository(db_path)
    return repo.get_provisioned_studies()


def render_auth_sidebar() -> bool:
    """Render sidebar authentication controls and update session auth state.

    Returns:
        ``True`` when a valid SDK connection is active in ``st.session_state``;
        otherwise ``False``.
    """
    with st.sidebar:
        st.header("🔐 Enterprise SSO")

        def on_env_change() -> None:
            clear_credentials()
            _mark_disconnected()

        env = st.selectbox(
            "Environment",
            options=["Default", "Dev", "UAT", "Prod"],
            key=_KEY_ENV,
            on_change=on_env_change,
        )

        if env == "Prod":
            st.error("🚨 Active Environment: PROD")
        elif env == "UAT":
            st.warning("⚠️ Active Environment: UAT")
        elif env == "Dev":
            st.success("🟢 Active Environment: DEV")

        # OIDC integration for corporate credentials
        is_logged_in = getattr(st.user, "is_logged_in", False) or "email" in getattr(st, "user", {})

        # Test mode bypass for browser E2E tests
        if os.environ.get("IMEDNET_BROWSER_TEST") == "1":
            is_logged_in = True
            if not hasattr(st, "user") or not st.user:

                class MockUser:
                    email = "test-operator@example.com"
                    is_logged_in = True

                st.user = MockUser()  # type: ignore[assignment]

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

        st.markdown(f"✅ **SSO Active:** {user_email}")

        studies = get_provisioned_studies()
        if not studies:
            st.warning("No studies available. Contact Global Admin to provision environments.")
            return False

        study_key = st.selectbox(
            "Select Authorized Study",
            options=studies,
            key=_KEY_STUDY_KEY,
            on_change=_mark_disconnected,
        )

        if st.session_state.get(_KEY_CONNECTED):
            if st.button("Disconnect", type="primary"):
                clear_credentials()
                st.rerun()
        elif st.button("Connect"):
            api_key, security_key, env_url = get_tenant_credentials(study_key)
            if not api_key or not security_key:
                st.error("Managed credentials for this tenant are missing.")
            else:
                try:
                    if os.environ.get("IMEDNET_BROWSER_TEST") == "1":
                        # In browser tests, we mock the SDK to avoid real network calls
                        from unittest.mock import MagicMock

                        st.session_state[_KEY_SDK] = MagicMock()
                    else:
                        _build_sdk(api_key=api_key, security_key=security_key, env_url=env_url)
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
    from typing import cast

    return cast('ImednetFacade', sdk)


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
    for key in (
        _KEY_API_KEY,
        _KEY_SECURITY_KEY,
        _KEY_STUDY_KEY,
        _KEY_SDK,
        _KEY_CONNECTED,
    ):
        st.session_state.pop(key, None)
    # Ensure cache is also purged when credentials are cleared
    st.cache_data.clear()
