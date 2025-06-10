from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class TemplateManager:
    """Manage save/load of command parameter templates."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path.home() / ".imednet_templates.json"

    def _load_all(self) -> Dict[str, Dict[str, str]]:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {}

    def _save_all(self, data: Dict[str, Dict[str, str]]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def save(self, name: str, params: Dict[str, str]) -> None:
        data = self._load_all()
        data[name] = params
        self._save_all(data)

    def load(self, name: str) -> Optional[Dict[str, str]]:
        return self._load_all().get(name)

    def list(self) -> List[str]:
        return sorted(self._load_all())

    def rename(self, old_name: str, new_name: str) -> None:
        data = self._load_all()
        if old_name not in data:
            raise KeyError(old_name)
        data[new_name] = data.pop(old_name)
        self._save_all(data)

    def delete(self, name: str) -> None:
        data = self._load_all()
        if name in data:
            del data[name]
            self._save_all(data)
