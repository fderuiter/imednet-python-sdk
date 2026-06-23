"""Tests for session isolation and cache behavior in Streamlit."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parents[3]
APP_PATH = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit" / "app.py"


@pytest.fixture
def mock_auth_env():
    """Set up mocks for authentication and studies."""
    with (
        patch("imednet_streamlit.auth.get_provisioned_studies", return_value=["STUDY-A", "STUDY-B"]),
        patch(
            "imednet_streamlit.auth.get_tenant_credentials",
            side_effect=lambda s: ("key-" + s, "sec-" + s),
        ) as mock_get_creds,
        patch("imednet_streamlit.auth.ImednetSDK") as mock_sdk,
        patch.dict(os.environ, {"IMEDNET_BROWSER_TEST": "1"}),
        patch("streamlit.cache_data.clear") as mock_cache_clear,
    ):
        yield mock_sdk, mock_cache_clear, mock_get_creds


def test_scenario_1_fresh_vs_connected_session(mock_auth_env) -> None:
    """Scenario 1: fresh session starts unauthenticated and connects after flow."""
    at = AppTest.from_file(str(APP_PATH))
    at.run()

    # Should not be connected initially
    assert "_imednet_connected" not in at.session_state or at.session_state["_imednet_connected"] is not True

    # Select the study and click connect
    at.sidebar.selectbox(key="_imednet_study_key").select("STUDY-A")
    connect_btn = next(b for b in at.sidebar.button if b.label == "Connect")
    connect_btn.click()
    at.run()

    assert at.session_state["_imednet_connected"] is True
    assert at.session_state["_imednet_study_key"] == "STUDY-A"


def test_scenario_2_disconnect_clears_state(mock_auth_env) -> None:
    """Scenario 2: clearing credentials removes session artifacts."""
    _, mock_cache_clear, _ = mock_auth_env
    from imednet_streamlit.auth import clear_credentials

    state = {
        "_imednet_api_key": "abc",
        "_imednet_security_key": "def",
        "_imednet_study_key": "STUDY-A",
        "_imednet_sdk": object(),
        "_imednet_connected": True,
    }
    with patch("imednet_streamlit.auth.st.session_state", state):
        clear_credentials()
        assert "_imednet_connected" not in state
        assert "_imednet_sdk" not in state
        assert "_imednet_study_key" not in state
        assert mock_cache_clear.called


def test_scenario_3_study_switch_disconnects(mock_auth_env) -> None:
    """Scenario 3: switching study context should disconnect the session."""
    at = AppTest.from_file(str(APP_PATH))
    at.run()
    at.sidebar.selectbox(key="_imednet_study_key").select("STUDY-A")
    connect_btn = next(b for b in at.sidebar.button if b.label == "Connect")
    connect_btn.click()
    at.run()

    assert at.session_state["_imednet_connected"] is True

    # Switch study
    at.sidebar.selectbox(key="_imednet_study_key").select("STUDY-B")
    at.run()

    # SHOULD be disconnected now because we don't want to use STUDY-A SDK with STUDY-B key
    connected = at.session_state["_imednet_connected"] if "_imednet_connected" in at.session_state else False
    assert connected is False


def test_scenario_4_cache_isolation(mock_auth_env) -> None:
    """Scenario 4: cache results are isolated (implicitly via SDK/study parameters)."""
    with patch("imednet_streamlit.auth.get_sdk"), patch("imednet_streamlit.auth.get_study_key"):
        from imednet_streamlit.pages.queries import _fetch_queries

    mock_sdk_a = MagicMock()
    mock_sdk_b = MagicMock()

    with patch("imednet_workflows.query_management.QueryManagementWorkflow") as mock_workflow_cls:
        _fetch_queries(mock_sdk_a, "STUDY-A")
        assert mock_workflow_cls.call_count == 1

        _fetch_queries(mock_sdk_a, "STUDY-A")
        assert mock_workflow_cls.call_count == 1

        _fetch_queries(mock_sdk_b, "STUDY-B")
        assert mock_workflow_cls.call_count == 2


def test_scenario_5_error_recovery(mock_auth_env) -> None:
    """Scenario 5: errors do not permanently poison the session."""
    _, _, mock_get_creds = mock_auth_env
    at = AppTest.from_file(str(APP_PATH))
    at.run()

    at.sidebar.selectbox(key="_imednet_study_key").select("STUDY-A")

    # 1. Simulate failure (missing credentials)
    mock_get_creds.side_effect = None
    mock_get_creds.return_value = (None, None)

    connect_btn = next(b for b in at.sidebar.button if b.label == "Connect")
    connect_btn.click()
    at.run()

    # Should show error and NOT be connected
    all_error_values = [e.value for e in at.error] + [e.value for e in at.sidebar.error]
    assert any("missing" in v for v in all_error_values)
    connected = at.session_state["_imednet_connected"] if "_imednet_connected" in at.session_state else False
    assert connected is not True

    # 2. Recover - provide valid credentials
    mock_get_creds.return_value = ("valid-key", "valid-sec")

    connect_btn = next(b for b in at.sidebar.button if b.label == "Connect")
    connect_btn.click()
    at.run()

    # Should now be connected
    assert at.session_state["_imednet_connected"] is True
    all_success_values = [s.value for s in at.success] + [s.value for s in at.sidebar.success]
    assert any("Connected ✓" in v for v in all_success_values)


def test_scenario_6_multi_session_isolation(mock_auth_env) -> None:
    """Scenario 6: concurrent user sessions remain independent."""
    at1 = AppTest.from_file(str(APP_PATH))
    at2 = AppTest.from_file(str(APP_PATH))

    at1.run()
    at2.run()

    # Connect session 1
    at1.sidebar.selectbox(key="_imednet_study_key").select("STUDY-A")
    connect_btn1 = next(b for b in at1.sidebar.button if b.label == "Connect")
    connect_btn1.click()
    at1.run()

    assert at1.session_state["_imednet_connected"] is True

    # Check session 2 status
    connected2 = at2.session_state["_imednet_connected"] if "_imednet_connected" in at2.session_state else False
    assert connected2 is not True

    # Connect session 2 to a different study
    at2.sidebar.selectbox(key="_imednet_study_key").select("STUDY-B")
    connect_btn2 = next(b for b in at2.sidebar.button if b.label == "Connect")
    connect_btn2.click()
    at2.run()

    assert at2.session_state["_imednet_connected"] is True
    assert at1.session_state["_imednet_study_key"] == "STUDY-A"
    assert at2.session_state["_imednet_study_key"] == "STUDY-B"
