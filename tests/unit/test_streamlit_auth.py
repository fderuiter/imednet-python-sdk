from __future__ import annotations

from types import SimpleNamespace

import pytest

from imednet_streamlit import auth


class _SidebarContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None


class _FakeStreamlit:
    def __init__(self, *, text_values: dict[str, str], connect_clicked: bool) -> None:
        self.session_state: dict[str, object] = {}
        self.sidebar = _SidebarContext()
        self._text_values = text_values
        self._connect_clicked = connect_clicked
        self.success_messages: list[str] = []
        self.error_messages: list[str] = []

    def header(self, _: str) -> None:
        pass

    def text_input(self, label: str, **kwargs: object) -> str:
        key = kwargs["key"]
        assert isinstance(key, str)
        value = self._text_values.get(label, "")
        self.session_state[key] = value
        return value

    def button(self, _: str) -> bool:
        return self._connect_clicked

    def success(self, message: str) -> None:
        self.success_messages.append(message)

    def error(self, message: str) -> None:
        self.error_messages.append(message)


def test_render_auth_sidebar_not_connected_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_st = _FakeStreamlit(text_values={}, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    assert auth.render_auth_sidebar() is False


def test_render_auth_sidebar_connects_and_clears_secret_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_st = _FakeStreamlit(
        text_values={"API Key": "api-key", "Security Key": "security-key", "Study Key": "STUDY"},
        connect_clicked=True,
    )
    monkeypatch.setattr(auth, "st", fake_st)
    sentinel_sdk = SimpleNamespace(name="sdk")

    def _fake_store_sdk(**_: object) -> None:
        fake_st.session_state[auth._KEY_SDK] = sentinel_sdk

    monkeypatch.setattr(
        auth,
        "_build_sdk",
        _fake_store_sdk,
    )

    assert auth.render_auth_sidebar() is True
    assert auth.get_sdk() is sentinel_sdk
    assert auth.get_study_key() == "STUDY"
    assert auth._KEY_API_KEY not in fake_st.session_state
    assert auth._KEY_SECURITY_KEY not in fake_st.session_state


def test_get_sdk_before_connect_raises_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_st = _FakeStreamlit(text_values={}, connect_clicked=False)
    monkeypatch.setattr(auth, "st", fake_st)

    with pytest.raises(RuntimeError):
        auth.get_sdk()


def test_clear_credentials_removes_all_session_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_st = _FakeStreamlit(text_values={}, connect_clicked=False)
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
    fake_st = _FakeStreamlit(
        text_values={"API Key": "api-key", "Security Key": "security-key", "Study Key": "STUDY"},
        connect_clicked=True,
    )
    monkeypatch.setattr(auth, "st", fake_st)

    def _raise_build_error(**_: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(auth, "_build_sdk", _raise_build_error)

    assert auth.render_auth_sidebar() is False
    assert auth._KEY_API_KEY not in fake_st.session_state
    assert auth._KEY_SECURITY_KEY not in fake_st.session_state
    assert auth._KEY_SDK not in fake_st.session_state
