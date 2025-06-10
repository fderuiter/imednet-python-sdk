from pathlib import Path

from cryptography.fernet import Fernet
from imednet.ui.credential_manager import ProfileManager


def test_profile_manager_crud(tmp_path: Path) -> None:
    path = tmp_path / "profiles"
    key = Fernet.generate_key()
    mgr = ProfileManager(path=path, key=key)

    mgr.save_profile("foo", "a", "b")
    mgr.save_profile("bar", "c", "d")

    assert set(mgr.list_profiles()) == {"foo", "bar"}

    mgr.set_current("foo")
    assert mgr.current() == "foo"

    loaded = mgr.load_profile()
    assert loaded == {
        "api_key": "a",
        "security_key": "b",
        "base_url": None,
        "study_key": None,
    }

    mgr.delete_profile("foo")
    assert "foo" not in mgr.list_profiles()
