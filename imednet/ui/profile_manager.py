from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet


class ProfileManager:
    """Manage multiple sets of encrypted credentials."""

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

    def _load_all(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"active": None, "profiles": {}}
        token = self.path.read_bytes()
        data = json.loads(self._fernet.decrypt(token).decode("utf-8"))
        if "profiles" not in data:
            # migrate from empty structure
            data = {"active": None, "profiles": {}}
        return data

    def _save_all(self, data: Dict[str, Any]) -> None:
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
        data = self._load_all()
        profiles = data.setdefault("profiles", {})
        profiles[name] = {
            "api_key": api_key,
            "security_key": security_key,
            "base_url": base_url,
            "study_key": study_key,
        }
        self._save_all(data)

    def load_profile(self, name: str) -> Optional[Dict[str, str | None]]:
        data = self._load_all()
        return data.get("profiles", {}).get(name)

    def list_profiles(self) -> List[str]:
        data = self._load_all()
        return sorted(data.get("profiles", {}))

    def delete_profile(self, name: str) -> None:
        data = self._load_all()
        profiles = data.get("profiles", {})
        if name in profiles:
            del profiles[name]
            if data.get("active") == name:
                data["active"] = None
            self._save_all(data)

    def rename_profile(self, old_name: str, new_name: str) -> None:
        data = self._load_all()
        profiles = data.get("profiles", {})
        if old_name not in profiles:
            raise KeyError(old_name)
        profiles[new_name] = profiles.pop(old_name)
        if data.get("active") == old_name:
            data["active"] = new_name
        self._save_all(data)

    def set_active(self, name: str) -> None:
        data = self._load_all()
        if name not in data.get("profiles", {}):
            raise KeyError(name)
        data["active"] = name
        self._save_all(data)

    def get_active_name(self) -> Optional[str]:
        data = self._load_all()
        return data.get("active")

    def load_active(self) -> Optional[Dict[str, str | None]]:
        name = self.get_active_name()
        if name is None:
            return None
        return self.load_profile(name)
