from pathlib import Path

from cryptography.fernet import Fernet
from imednet.ui.credential_manager import CredentialManager


def test_save_and_load_credentials(tmp_path: Path) -> None:
    cred_path = tmp_path / "creds"
    key = Fernet.generate_key()
    manager = CredentialManager(path=cred_path, key=key)

    manager.save("a", "b", "http://example.com", "STUDY")
    loaded = manager.load()

    assert loaded == {
        "api_key": "a",
        "security_key": "b",
        "base_url": "http://example.com",
        "study_key": "STUDY",
    }
