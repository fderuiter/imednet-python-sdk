from imednet import credentials
from imednet.credentials import load_credentials, resolve_credentials, save_credentials


def test_save_and_load(tmp_path):
    path = tmp_path / "cred.enc"
    save_credentials("a", "b", "c", "pass", path)
    creds = load_credentials("pass", path)
    assert creds == {"api_key": "a", "security_key": "b", "study_key": "c"}


def test_resolve_credentials_from_env(monkeypatch):
    monkeypatch.setenv("IMEDNET_API_KEY", "env_api")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "env_sec")
    monkeypatch.setenv("IMEDNET_STUDY_KEY", "ENVSTUDY")
    assert resolve_credentials("pass") == ("env_api", "env_sec", "ENVSTUDY")


def test_resolve_credentials_from_file(tmp_path, monkeypatch):
    path = tmp_path / "cred.enc"
    save_credentials("file_api", "file_sec", "FILESTUDY", "pwd", path)
    monkeypatch.setattr(credentials, "CREDENTIALS_FILE", path)
    monkeypatch.delenv("IMEDNET_API_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_SECURITY_KEY", raising=False)
    monkeypatch.delenv("IMEDNET_STUDY_KEY", raising=False)
    assert resolve_credentials("pwd") == ("file_api", "file_sec", "FILESTUDY")
