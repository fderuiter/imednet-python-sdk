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


def test_dashboard_shows_auth_prompt_when_not_connected() -> None:
    at = AppTest.from_file(str(APP_PATH))
    at.run()

    assert at.title[0].value == "🏥 iMednet EDC Dashboard"
    message = at.info[0].value.lower()
    assert "authenticate" in message
    assert "sidebar" in message


def test_dashboard_login_uses_sdk_after_credentials_entered() -> None:
    """Successful login should connect and clear raw credential inputs from session state."""
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
    success_message = at.success[0].value
    assert "Connected to study:" in success_message
    assert "PROT-100" in success_message
    assert at.session_state["_imednet_connected"] is True
    assert "_imednet_api_key" not in at.session_state
    assert "_imednet_security_key" not in at.session_state
