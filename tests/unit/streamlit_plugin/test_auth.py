"""Unit tests for auth."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from imednet_streamlit import auth


class _SidebarContext:
    """Test suite for  SidebarContext."""

    def __enter__(self) -> None:
        """Helper function to   enter  ."""
        return

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Helper function to   exit  ."""
        return


class _FakeCacheData:
    """Test suite for  FakeCacheData."""

    def clear(self) -> None:
        """Helper function to clear."""


class _FakeStreamlit:
    """Test suite for  FakeStreamlit."""

    def __init__(
        self,
        *,
        logged_in: bool = False,
        connect_clicked: bool = False,
        selected_study: str = "STUDY",
    ) -> None:
        """Initialize the test object."""
        self.session_state: dict[str, object] = {}
        self.sidebar = _SidebarContext()
        self._connect_clicked = connect_clicked
        self.success_messages: list[str] = []
        self.markdown_messages: list[str] = []
        self.error_messages: list[str] = []
        self.warning_messages: list[str] = []
        self.info_messages: list[str] = []
        self.cache_data = _FakeCacheData()

        self.user = {"email": "test@enterprise.com", "is_logged_in": logged_in} if logged_in else {}
        self.login_called = False
        self._selected_study = selected_study

    def header(self, _: str) -> None:
        """Helper function to header."""

    def text_input(self, label: str, **kwargs: object) -> str:
        """Helper function to text input."""
        key = kwargs["key"]
        self.session_state[key] = ""
        return ""

    def selectbox(self, label: str, options: list[str], key: str, **kwargs: object) -> str:
        """Helper function to selectbox."""
        self.session_state[key] = self._selected_study
        return self._selected_study

    def button(self, _: str, **kwargs: object) -> bool:
        """Helper function to button."""
        return self._connect_clicked

    def rerun(self) -> None:
        """Helper function to rerun."""

    def markdown(self, message: str) -> None:
        self.markdown_messages.append(message)

    def success(self, message: str) -> None:
        """Helper function to success."""
        self.success_messages.append(message)

    def error(self, message: str) -> None:
        """Helper function to error."""
        self.error_messages.append(message)

    def warning(self, message: str) -> None:
        """Helper function to warning."""
        self.warning_messages.append(message)

    def info(self, message: str) -> None:
        """Helper function to info."""
        self.info_messages.append(message)

    def login(self) -> None:
        """Helper function to login."""
        self.login_called = True


def test_render_auth_sidebar_not_connected_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that render auth sidebar not connected returns false."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    assert auth.render_auth_sidebar() is False
    assert len(fake_st.info_messages) > 0


def test_render_auth_sidebar_connects_and_clears_secret_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that render auth sidebar connects and clears secret keys."""
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=True, selected_study="STUDY")
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])
    monkeypatch.setattr(auth, "get_tenant_credentials", lambda x: ("api", "sec", None))
    sentinel_sdk = SimpleNamespace(name="sdk")

    def _fake_store_sdk(**_: object) -> None:
        """Helper function to  fake store sdk."""
        fake_st.session_state[auth._KEY_SDK] = sentinel_sdk

    monkeypatch.setattr(
        auth,
        "_build_sdk",
        _fake_store_sdk,
    )

    assert auth.render_auth_sidebar() is True
    assert auth.get_sdk() is sentinel_sdk
    assert auth.get_study_key() == "STUDY"


def test_get_sdk_before_connect_raises_runtime_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that get sdk before connect raises runtime error."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    with pytest.raises(RuntimeError):
        auth.get_sdk()


def test_clear_credentials_removes_all_session_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that clear credentials removes all session keys."""
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
    """Test that render auth sidebar build failure clears secret keys."""
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=True)
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])
    monkeypatch.setattr(auth, "get_tenant_credentials", lambda x: ("api", "sec", None))

    def _raise_build_error(**_: object) -> None:
        """Helper function to  raise build error."""
        raise RuntimeError("boom")

    monkeypatch.setattr(auth, "_build_sdk", _raise_build_error)

    assert auth.render_auth_sidebar() is False
    assert auth._KEY_SDK not in fake_st.session_state


def test_render_auth_sidebar_missing_fields_marks_disconnected_and_clears_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that render auth sidebar missing fields marks disconnected and clears secrets."""
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=True)
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])
    monkeypatch.setattr(auth, "get_tenant_credentials", lambda x: (None, None, None))

    result = auth.render_auth_sidebar()

    assert result is False
    assert fake_st.session_state.get(auth._KEY_CONNECTED) is not True
    assert auth._KEY_SDK not in fake_st.session_state
    assert len(fake_st.error_messages) > 0
    assert "Managed credentials" in fake_st.error_messages[0]


def test_build_sdk_calls_sdk_init(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that build sdk calls sdk init."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    sdk_args = {}

    class FakeSDK:
        """Test suite for FakeSDK."""

        def __init__(self, api_key: str, security_key: str, base_url: str | None = None) -> None:
            """Initialize the test object."""
            sdk_args["api_key"] = api_key
            sdk_args["security_key"] = security_key
            sdk_args["base_url"] = base_url

    monkeypatch.setattr(auth, "ImednetSDK", FakeSDK)

    auth._build_sdk("key1", "key2")
    assert sdk_args == {"api_key": "key1", "security_key": "key2", "base_url": None}
    assert isinstance(fake_st.session_state[auth._KEY_SDK], FakeSDK)


def test_get_study_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that get study key raises when missing."""
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    with pytest.raises(RuntimeError, match="Study key is not set"):
        auth.get_study_key()


import sqlite3


def test_get_tenant_credentials_no_db(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("IMEDNET_TENANT_DB_PATH", str(tmp_path / "missing.sqlite3"))
    assert auth.get_tenant_credentials("S") == (None, None, None)


def test_get_tenant_credentials_with_db(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    db_path = tmp_path / "db.sqlite3"
    monkeypatch.setenv("IMEDNET_TENANT_DB_PATH", str(db_path))
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE tenants (study_key TEXT, api_key TEXT, security_key TEXT)")
        conn.execute("INSERT INTO tenants VALUES ('S1', 'a1', 's1')")

    # Should migrate env_url and fetch
    assert auth.get_tenant_credentials("S1") == ("a1", "s1", None)

    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE tenants SET env_url='http://env' WHERE study_key='S1'")
    assert auth.get_tenant_credentials("S1") == ("a1", "s1", "http://env")


def test_get_provisioned_studies_no_db(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("IMEDNET_TENANT_DB_PATH", str(tmp_path / "missing.sqlite3"))
    assert auth.get_provisioned_studies() == []


def test_get_provisioned_studies_with_db(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    db_path = tmp_path / "db.sqlite3"
    monkeypatch.setenv("IMEDNET_TENANT_DB_PATH", str(db_path))
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE tenants (study_key TEXT)")
        conn.execute("INSERT INTO tenants VALUES ('S1')")
        conn.execute("INSERT INTO tenants VALUES ('S2')")

    assert auth.get_provisioned_studies() == ["S1", "S2"]


def test_get_provisioned_studies_db_error(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    db_path = tmp_path / "db.sqlite3"
    monkeypatch.setenv("IMEDNET_TENANT_DB_PATH", str(db_path))
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE different (study_key TEXT)")

    assert auth.get_provisioned_studies() == []


def test_render_auth_sidebar_no_login_method_fixed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=False)

    # create a mock that does not have login
    class NoLoginSt:
        user = {}
        sidebar = _FakeStreamlit().sidebar

        @staticmethod
        def header(msg):
            pass

        @staticmethod
        def info(msg):
            fake_st.info(msg)

        @staticmethod
        def warning(msg):
            fake_st.warning(msg)

        @staticmethod
        def selectbox(*args, **kwargs):
            return "Default"

        @staticmethod
        def error(msg):
            pass

        @staticmethod
        def success(msg):
            pass

    monkeypatch.setattr(auth, "st", NoLoginSt)
    assert auth.render_auth_sidebar() is False
    assert len(fake_st.warning_messages) > 0


def test_auth_py_misc_coverage(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=False)

    # mock get missing email
    class MockUserDict(dict):
        pass

    fake_st.user = MockUserDict()

    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])

    assert auth.render_auth_sidebar() is False


def test_render_auth_sidebar_connect_disconnect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=True)
    fake_st.session_state[auth._KEY_CONNECTED] = True
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])
    monkeypatch.setattr(auth, "clear_credentials", lambda: None)

    assert auth.render_auth_sidebar() is True


def test_render_auth_sidebar_no_studies(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_st = _FakeStreamlit(logged_in=True, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", list)
    assert auth.render_auth_sidebar() is False
    assert len(fake_st.warning_messages) > 0


def test_render_auth_sidebar_browser_test(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMEDNET_BROWSER_TEST", "1")
    fake_st = _FakeStreamlit(logged_in=False, connect_clicked=True)
    fake_st.user = {}
    monkeypatch.setattr(auth, "st", fake_st)
    monkeypatch.setattr(auth, "get_provisioned_studies", lambda: ["STUDY"])
    monkeypatch.setattr(auth, "get_tenant_credentials", lambda x: ("api", "sec", None))
    monkeypatch.setattr(auth, "_build_sdk", lambda *args, **kwargs: None)

    assert auth.render_auth_sidebar() is True
    assert fake_st.user.email == "test-operator@example.com"
