"""Unit tests for pages admin."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

repo_root = Path(__file__).resolve().parents[3]
package_root = repo_root / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"


def test_admin_page_renders():
    """Test that admin page renders."""
    page_path = package_root / "pages" / "admin.py"

    fake_st = MagicMock()
    fake_st.session_state = {"_imednet_connected": True}

    fake_auth = MagicMock()
    mock_sdk = MagicMock()
    fake_auth.get_sdk.return_value = mock_sdk

    prev_st = sys.modules.get("streamlit")
    prev_auth = sys.modules.get("imednet_streamlit.auth")
    prev_admin = sys.modules.get("imednet_streamlit.pages.admin")

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
        if prev_st is not None:
            sys.modules["streamlit"] = prev_st
        else:
            sys.modules.pop("streamlit", None)

        if prev_auth is not None:
            sys.modules["imednet_streamlit.auth"] = prev_auth
        else:
            sys.modules.pop("imednet_streamlit.auth", None)

        if prev_admin is not None:
            sys.modules["imednet_streamlit.pages.admin"] = prev_admin
        else:
            sys.modules.pop("imednet_streamlit.pages.admin", None)


import importlib.util
import sys
from pathlib import Path

import pytest


def _run_admin(fake_st):
    repo_root = Path(__file__).resolve().parents[3]
    package_root = repo_root / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"
    page_path = package_root / "pages" / "admin.py"

    prev_st = sys.modules.get("streamlit")
    sys.modules["streamlit"] = fake_st

    spec = importlib.util.spec_from_file_location("imednet_streamlit.pages.admin", str(page_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["imednet_streamlit.pages.admin"] = mod

    try:
        spec.loader.exec_module(mod)
    finally:
        if prev_st is not None:
            sys.modules["streamlit"] = prev_st
        else:
            sys.modules.pop("streamlit", None)


class FakeStMockAdmin:
    def __init__(self, logged_in=True):
        self.success_messages = []
        self.error_messages = []
        self.session_state = {}

    def title(self, msg):
        pass

    def markdown(self, msg):
        pass

    def success(self, msg):
        self.success_messages.append(msg)

    def error(self, msg):
        self.error_messages.append(msg)


def test_admin_page_provision_success(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    db_path = tmp_path / "db.sqlite3"
    monkeypatch.setenv("IMEDNET_TENANT_DB_PATH", str(db_path))

    class FakeSt(FakeStMockAdmin):
        def text_input(self, label: str, **kwargs: object) -> str:
            if "Study" in label:
                return "S1"
            if "API" in label:
                return "A1"
            if "Security" in label:
                return "SEC1"
            if "URL" in label:
                return "http://env"
            return ""

        def button(self, _: str, **kwargs: object) -> bool:
            return True

    fake_st = FakeSt(logged_in=True)
    _run_admin(fake_st)
    print("ERRORS:", fake_st.error_messages)
    assert len(fake_st.success_messages) > 0

    _run_admin(fake_st)
    assert len(fake_st.success_messages) > 1


def test_admin_page_provision_missing_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSt(FakeStMockAdmin):
        def text_input(self, label: str, **kwargs: object) -> str:
            return ""

        def button(self, _: str, **kwargs: object) -> bool:
            return True

    fake_st = FakeSt(logged_in=True)
    _run_admin(fake_st)
    assert len(fake_st.error_messages) > 0


def test_admin_page_provision_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSt(FakeStMockAdmin):
        def text_input(self, label: str, **kwargs: object) -> str:
            return "valid"

        def button(self, _: str, **kwargs: object) -> bool:
            return True

    fake_st = FakeSt(logged_in=True)

    def raise_boom(*args, **kwargs):
        raise RuntimeError("boom")

    from imednet_streamlit.credentials import CredentialRepository

    monkeypatch.setattr(CredentialRepository, "provision_tenant", raise_boom)

    _run_admin(fake_st)
    assert len(fake_st.error_messages) > 0
