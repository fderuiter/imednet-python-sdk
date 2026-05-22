from __future__ import annotations

import streamlit as st

from imednet import ImednetSDK
from imednet.auth import ApiKeyAuth

_KEY_API_KEY = "_imednet_api_key"
_KEY_SECURITY_KEY = "_imednet_security_key"
_KEY_STUDY_KEY = "_imednet_study_key"
_KEY_SDK = "_imednet_sdk"
_KEY_CONNECTED = "_imednet_connected"

__all__ = ["render_auth_sidebar", "get_sdk", "get_study_key", "clear_credentials"]


def _build_sdk(api_key: str, security_key: str) -> None:
    """Construct and cache an authenticated SDK instance."""
    auth = ApiKeyAuth(api_key=api_key, security_key=security_key)
    st.session_state[_KEY_SDK] = ImednetSDK(
        api_key=auth.api_key,
        security_key=auth.security_key,
    )


def _mark_disconnected() -> None:
    st.session_state[_KEY_CONNECTED] = False
    st.session_state.pop(_KEY_SDK, None)


def render_auth_sidebar() -> bool:
    """
    Render auth controls in the Streamlit sidebar and cache an SDK when connected.
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
                except Exception:
                    _mark_disconnected()
                    st.error("Connection failed.")
                else:
                    st.session_state[_KEY_CONNECTED] = True
                    st.success("Connected ✓")
                finally:
                    st.session_state.pop(_KEY_API_KEY, None)
                    st.session_state.pop(_KEY_SECURITY_KEY, None)
            else:
                _mark_disconnected()
                st.error("All fields are required.")

    return bool(st.session_state.get(_KEY_CONNECTED))


def get_sdk() -> ImednetSDK:
    """Return the authenticated SDK from session state."""
    sdk = st.session_state.get(_KEY_SDK)
    if not st.session_state.get(_KEY_CONNECTED) or sdk is None:
        raise RuntimeError("SDK is not connected. Call render_auth_sidebar() first.")
    return sdk


def get_study_key() -> str:
    """Return the selected study key from session state."""
    study_key = st.session_state.get(_KEY_STUDY_KEY)
    if not isinstance(study_key, str) or not study_key:
        raise RuntimeError("Study key is not set. Call render_auth_sidebar() first.")
    return study_key


def clear_credentials() -> None:
    """Remove all auth-related state from the Streamlit session."""
    for key in (_KEY_API_KEY, _KEY_SECURITY_KEY, _KEY_STUDY_KEY, _KEY_SDK, _KEY_CONNECTED):
        st.session_state.pop(key, None)
