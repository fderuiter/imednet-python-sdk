from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet


class CredentialManager:
    """Handles encryption and storage of credentials."""

    def __init__(self, path: Optional[Path] = None, key: Optional[bytes] = None) -> None:
        self.path = path or Path.home() / ".imednet_credentials"
        if key is None:
            key_file = self.path.with_suffix(".key")
            if key_file.exists():
                key = key_file.read_bytes()
            else:
                key = Fernet.generate_key()
                key_file.write_bytes(key)
        self._fernet = Fernet(key)

    def save(
        self,
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        study_key: Optional[str] = None,
    ) -> None:
        data = {
            "api_key": api_key,
            "security_key": security_key,
            "base_url": base_url,
            "study_key": study_key,
        }
        token = self._fernet.encrypt(json.dumps(data).encode("utf-8"))
        self.path.write_bytes(token)

    def load(self) -> Optional[dict[str, str | None]]:
        if not self.path.exists():
            return None
        token = self.path.read_bytes()
        payload = self._fernet.decrypt(token)
        data = json.loads(payload.decode("utf-8"))
        return data


class ProfileManager:
    """Manage multiple named credential profiles using encryption."""

    def __init__(self, path: Optional[Path] = None, key: Optional[bytes] = None) -> None:
        self.path = path or Path.home() / ".imednet_profiles"
        if key is None:
            key_file = self.path.with_suffix(".key")
            if key_file.exists():
                key = key_file.read_bytes()
            else:
                key = Fernet.generate_key()
                key_file.write_bytes(key)
        self._fernet = Fernet(key)

    def _read(self) -> dict:
        if not self.path.exists():
            return {"current": None, "profiles": {}}
        token = self.path.read_bytes()
        data = json.loads(self._fernet.decrypt(token).decode("utf-8"))
        if "profiles" not in data:
            data = {"current": None, "profiles": {"default": data}}
        return data

    def _write(self, data: dict) -> None:
        token = self._fernet.encrypt(json.dumps(data).encode("utf-8"))
        self.path.write_bytes(token)

    def save_profile(
        self,
        name: str,
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        study_key: Optional[str] = None,
    ) -> None:
        data = self._read()
        data.setdefault("profiles", {})[name] = {
            "api_key": api_key,
            "security_key": security_key,
            "base_url": base_url,
            "study_key": study_key,
        }
        self._write(data)

    def load_profile(self, name: Optional[str] = None) -> Optional[dict[str, str | None]]:
        data = self._read()
        name = name or data.get("current")
        if not name:
            return None
        return data.get("profiles", {}).get(name)

    def delete_profile(self, name: str) -> None:
        data = self._read()
        if name in data.get("profiles", {}):
            del data["profiles"][name]
            if data.get("current") == name:
                data["current"] = None
            self._write(data)

    def list_profiles(self) -> list[str]:
        data = self._read()
        return list(data.get("profiles", {}).keys())

    def set_current(self, name: str) -> None:
        data = self._read()
        if name not in data.get("profiles", {}):
            raise KeyError(name)
        data["current"] = name
        self._write(data)

    def current(self) -> Optional[str]:
        data = self._read()
        return data.get("current")
