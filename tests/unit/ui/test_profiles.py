from pathlib import Path

from cryptography.fernet import Fernet
from imednet.ui.profile_manager import ProfileManager


def test_profile_crud(tmp_path: Path) -> None:
    path = tmp_path / "profiles"
    key = Fernet.generate_key()
    mgr = ProfileManager(path=path, key=key)

    mgr.save_profile("p1", "a", "b")
    assert mgr.load_profile("p1") == {
        "api_key": "a",
        "security_key": "b",
        "base_url": None,
        "study_key": None,
    }
    assert mgr.list_profiles() == ["p1"]

    mgr.rename_profile("p1", "p2")
    assert mgr.list_profiles() == ["p2"]

    mgr.delete_profile("p2")
    assert mgr.list_profiles() == []


def test_active_profile(tmp_path: Path) -> None:
    path = tmp_path / "profiles"
    key = Fernet.generate_key()
    mgr = ProfileManager(path=path, key=key)

    mgr.save_profile("p1", "a", "b")
    mgr.save_profile("p2", "c", "d")
    mgr.set_active("p2")
    assert mgr.get_active_name() == "p2"
    assert mgr.load_active() == {
        "api_key": "c",
        "security_key": "d",
        "base_url": None,
        "study_key": None,
    }
