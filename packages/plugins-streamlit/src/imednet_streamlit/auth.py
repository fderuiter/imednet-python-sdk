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
    st.session_state[_KEY_CONNECTED] = False
    st.session_state.pop(_KEY_SDK, None)


def render_auth_sidebar() -> bool:
    """Render sidebar authentication controls and update session auth state.

    Returns:
        ``True`` when a valid SDK connection is active in ``st.session_state``;
        otherwise ``False``.
    """
    with st.sidebar:
        st.header("🔐 Authentication")
        api_key = st.text_input("API Key", type="password", key=_KEY_API_KEY)
        security_key = st.text_input("Security Key", type="password", key=_KEY_SECURITY_KEY)
        study_key = st.text_input("Study Key", key=_KEY_STUDY_KEY)

        if st.button("Connect"):
            if api_key and security_key and study_key:
                try:
                    _build_sdk(api_key=api_key, security_key=security_key)
                except Exception as exc:
                    _mark_disconnected()
                    st.error(f"Connection failed ({type(exc).__name__}).")
                else:
                    st.session_state[_KEY_CONNECTED] = True
                    st.success("Connected ✓")
                finally:
                    st.session_state.pop(_KEY_API_KEY, None)
                    st.session_state.pop(_KEY_SECURITY_KEY, None)
            else:
                _mark_disconnected()
                st.session_state.pop(_KEY_API_KEY, None)
                st.session_state.pop(_KEY_SECURITY_KEY, None)
                st.error("All fields are required.")

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
