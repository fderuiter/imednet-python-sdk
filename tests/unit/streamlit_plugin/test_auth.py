"""Test Auth module."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from imednet_streamlit import auth


class _SidebarContext:
    """Test suite for _SidebarContext."""

    def __enter__(self) -> None:
        """Test the enter functionality."""
        return None

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Test the exit functionality."""
        return None


class _FakeCacheData:
    """Test suite for _FakeCacheData."""

    def clear(self) -> None:
        """Test the clear functionality."""
        pass


class _FakeStreamlit:
    """Test suite for _FakeStreamlit."""

    def __init__(
        self,
        *,
        logged_in: bool = False,
        connect_clicked: bool = False,
        selected_study: str = "STUDY",
    ) -> None:
        """Implementation detail."""
        self.session_state: dict[str, object] = {}
        self.sidebar = _SidebarContext()
        self._connect_clicked = connect_clicked
        self.success_messages: list[str] = []
        self.error_messages: list[str] = []
        self.warning_messages: list[str] = []
        self.info_messages: list[str] = []
        self.cache_data = _FakeCacheData()

        self.user = {"email": "test@enterprise.com", "is_logged_in": logged_in} if logged_in else {}
        self.login_called = False
        self._selected_study = selected_study

    def header(self, _: str) -> None:
        """Test the header functionality."""
        pass

    def text_input(self, label: str, **kwargs: object) -> str:
        """Test the text input functionality."""
        key = kwargs["key"]
        self.session_state[key] = ""
        return ""

    def selectbox(self, label: str, options: list[str], key: str, **kwargs: object) -> str:
        """Test the selectbox functionality."""
        self.session_state[key] = self._selected_study
        return self._selected_study

    def button(self, _: str, **kwargs: object) -> bool:
        """Test the button functionality."""
        return self._connect_clicked

    def rerun(self) -> None:
        """Test the rerun functionality."""
        pass

    def success(self, message: str) -> None:
        """Test the success functionality."""
        self.success_messages.append(message)

    def error(self, message: str) -> None:
        """Test the error functionality."""
        self.error_messages.append(message)

    def warning(self, message: str) -> None:
        """Test the warning functionality."""
        self.warning_messages.append(message)

    def info(self, message: str) -> None:
        """Test the info functionality."""
        self.info_messages.append(message)

    def login(self) -> None:
        """Test the login functionality."""
        self.login_called = True


def test_render_auth_sidebar_not_connected_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the test render auth sidebar not connected returns false functionality."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    assert auth.render_auth_sidebar() is False
    assert len(fake_st.info_messages) > 0


def test_render_auth_sidebar_connects_and_clears_secret_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the test render auth sidebar connects and clears secret keys functionality."""
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=True, selected_study="STUDY")
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])
    monkeypatch.setattr(auth, "get_tenant_credentials", lambda x: ("api", "sec"))
    sentinel_sdk = SimpleNamespace(name="sdk")

    def _fake_store_sdk(**_: object) -> None:
        """Test the fake store sdk functionality."""
        fake_st.session_state[auth._KEY_SDK] = sentinel_sdk

    monkeypatch.setattr(
        auth,
        "_build_sdk",
        _fake_store_sdk,
    )

    assert auth.render_auth_sidebar() is True
    assert auth.get_sdk() is sentinel_sdk
    assert auth.get_study_key() == "STUDY"


def test_get_sdk_before_connect_raises_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the test get sdk before connect raises runtime error functionality."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    with pytest.raises(RuntimeError):
        auth.get_sdk()


def test_clear_credentials_removes_all_session_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the test clear credentials removes all session keys functionality."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    fake_st.session_state.update(
        {
            auth._KEY_API_KEY: "api-key",
            auth._KEY_SECURITY_KEY: "security-key",
            auth._KEY_STUDY_KEY: "STUDY",
            auth._KEY_SDK: object(),
            auth._KEY_CONNECTED: True,
        }
    )
    monkeypatch.setattr(auth, "st", fake_st)

    auth.clear_credentials()

    assert fake_st.session_state == {}


def test_render_auth_sidebar_build_failure_clears_secret_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the test render auth sidebar build failure clears secret keys functionality."""
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=True)
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])
    monkeypatch.setattr(auth, "get_tenant_credentials", lambda x: ("api", "sec"))

    def _raise_build_error(**_: object) -> None:
        """Test the raise build error functionality."""
        raise RuntimeError("boom")

    monkeypatch.setattr(auth, "_build_sdk", _raise_build_error)

    assert auth.render_auth_sidebar() is False
    assert auth._KEY_SDK not in fake_st.session_state


def test_render_auth_sidebar_missing_fields_marks_disconnected_and_clears_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the test render auth sidebar missing fields marks disconnected and clears secrets functionality."""
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=True)
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])
    monkeypatch.setattr(auth, "get_tenant_credentials", lambda x: (None, None))

    result = auth.render_auth_sidebar()

    assert result is False
    assert fake_st.session_state.get(auth._KEY_CONNECTED) is not True
    assert auth._KEY_SDK not in fake_st.session_state
    assert len(fake_st.error_messages) > 0
    assert "Managed credentials" in fake_st.error_messages[0]


def test_build_sdk_calls_sdk_init(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the test build sdk calls sdk init functionality."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    sdk_args = {}

    class FakeSDK:
        """Test suite for FakeSDK."""

        def __init__(self, api_key: str, security_key: str) -> None:
            """Initialize a new instance."""
            sdk_args["api_key"] = api_key
            sdk_args["security_key"] = security_key

    monkeypatch.setattr(auth, "ImednetSDK", FakeSDK)

    auth._build_sdk("key1", "key2")
    assert sdk_args == {"api_key": "key1", "security_key": "key2"}
    assert isinstance(fake_st.session_state[auth._KEY_SDK], FakeSDK)


def test_get_study_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the test get study key raises when missing functionality."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    with pytest.raises(RuntimeError, match="Study key is not set"):
        auth.get_study_key()
