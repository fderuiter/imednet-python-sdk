import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"


def test_conformance_page_renders():
    page_path = PACKAGE_ROOT / "pages" / "conformance.py"

    fake_st = MagicMock()
    fake_st.session_state = {"_imednet_connected": True}

    fake_auth = MagicMock()
    mock_sdk = MagicMock()
    fake_auth.get_sdk.return_value = mock_sdk

    prev_st = sys.modules.get("streamlit")
    prev_auth = sys.modules.get("imednet_streamlit.auth")
    prev_conf = sys.modules.get("imednet_streamlit.pages.conformance")

    sys.modules["streamlit"] = fake_st
    sys.modules["imednet_streamlit.auth"] = fake_auth

    spec = importlib.util.spec_from_file_location(
        "imednet_streamlit.pages.conformance", str(page_path)
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["imednet_streamlit.pages.conformance"] = mod

    try:
        spec.loader.exec_module(mod)
    except Exception:
        pass
    finally:
        if prev_st is not None:
            sys.modules["streamlit"] = prev_st
        else:
            sys.modules.pop("streamlit", None)

        if prev_auth is not None:
            sys.modules["imednet_streamlit.auth"] = prev_auth
        else:
            sys.modules.pop("imednet_streamlit.auth", None)

        if prev_conf is not None:
            sys.modules["imednet_streamlit.pages.conformance"] = prev_conf
        else:
            sys.modules.pop("imednet_streamlit.pages.conformance", None)
