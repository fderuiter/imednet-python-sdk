"""TODO: Add docstring."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parents[3]
APP_PATH = (
    REPO_ROOT
    / "packages"
    / "plugins-streamlit"
    / "src"
    / "imednet_streamlit"
    / "app.py"
)


def test_dashboard_login_requires_all_fields() -> None:
    """TODO: Add docstring."""
    # We mock studies so the form renders, but mock credentials so it fails.
    with (
        patch(
            "imednet_streamlit.auth.get_provisioned_studies", return_value=["PROT-100"]
        ),
        patch(
            "imednet_streamlit.auth.get_tenant_credentials", return_value=(None, None)
        ),
    ):
        at = AppTest.from_file(str(APP_PATH))
        at.run()

        # Click connect
        at.sidebar.button[0].click()
        at.run()

        # It should display an error about missing credentials
        assert (
            "Managed credentials for this tenant are missing"
            in at.sidebar.error[0].value
        )


def test_dashboard_shows_auth_prompt_when_not_connected() -> None:
    """TODO: Add docstring."""
    at = AppTest.from_file(str(APP_PATH))
    at.run()

    assert at.title[0].value == "🏥 iMednet EDC Dashboard"
    message = at.info[0].value.lower()
    assert "authenticate" in message
    assert "sidebar" in message


def test_dashboard_login_uses_sdk_after_credentials_entered() -> None:
    """Successful login should connect using managed credentials."""
    with (
        patch("imednet_streamlit.auth.ImednetSDK") as mock_sdk,
        patch(
            "imednet_streamlit.auth.get_provisioned_studies", return_value=["PROT-100"]
        ),
        patch(
            "imednet_streamlit.auth.get_tenant_credentials",
            return_value=("test-api", "test-sec"),
        ),
    ):
        at = AppTest.from_file(str(APP_PATH))
        # Mock SSO logged in
        at.session_state["_imednet_user_mock"] = True
        with patch(
            "imednet_streamlit.auth.getattr",
            side_effect=lambda obj, name, default=None: (
                True if name == "is_logged_in" else default
            ),
        ):
            at.run()

            # Select the study and connect
            # Selectbox is at index 0 in the main area or sidebar
            at.sidebar.selectbox[0].select("PROT-100")
            at.sidebar.button[0].click()
            at.run()

    assert mock_sdk.called
    assert at.sidebar.success[1].value == "Connected ✓"
    success_message = at.success[0].value
    assert "Connected to study:" in success_message
    assert "PROT-100" in success_message
    assert at.session_state["_imednet_connected"] is True
