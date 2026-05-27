from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parents[3]
APP_PATH = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit" / "app.py"


def test_dashboard_login_requires_all_fields() -> None:
    at = AppTest.from_file(str(APP_PATH))
    at.run()

    at.sidebar.button[0].click()
    at.run()

    assert at.sidebar.error[0].value == "All fields are required."


def test_dashboard_login_uses_sdk_after_credentials_entered() -> None:
    with patch("imednet_streamlit.auth.ImednetSDK") as mock_sdk:
        at = AppTest.from_file(str(APP_PATH))
        at.run()

        at.sidebar.text_input(key="_imednet_api_key").input("test-api-key")
        at.sidebar.text_input(key="_imednet_security_key").input("test-security-key")
        at.sidebar.text_input(key="_imednet_study_key").input("PROT-100")
        at.sidebar.button[0].click()
        at.run()

    assert mock_sdk.called
    assert at.sidebar.success[0].value == "Connected ✓"
