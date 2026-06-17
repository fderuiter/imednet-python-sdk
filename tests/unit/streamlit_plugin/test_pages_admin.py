import pytest
import sys
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"

def test_admin_page_renders():
    page_path = PACKAGE_ROOT / "pages" / "admin.py"
    
    fake_st = MagicMock()
    fake_st.session_state = {"_imednet_connected": True}
    
    fake_auth = MagicMock()
    mock_sdk = MagicMock()
    fake_auth.get_sdk.return_value = mock_sdk
    
    sys.modules["streamlit"] = fake_st
    sys.modules["imednet_streamlit.auth"] = fake_auth
    
    spec = importlib.util.spec_from_file_location("imednet_streamlit.pages.admin", str(page_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["imednet_streamlit.pages.admin"] = mod
    
    try:
        spec.loader.exec_module(mod)
    except Exception:
        pass
    finally:
        sys.modules.pop("streamlit", None)
        sys.modules.pop("imednet_streamlit.auth", None)
        sys.modules.pop("imednet_streamlit.pages.admin", None)
