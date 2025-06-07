"""Utilities for loading Veeva Vault mapping configurations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import import_module
from typing import TYPE_CHECKING, Any, Callable, Mapping

if TYPE_CHECKING:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
else:  # pragma: no cover - optional dependency
    try:
        import yaml  # type: ignore
    except Exception:  # pragma: no cover - yaml may not be installed
        yaml = None  # type: ignore


@dataclass
class MappingConfig:
    """Mapping configuration loaded from a JSON or YAML file."""

    mapping: dict[str, str]
    defaults: dict[str, Any]
    transforms: dict[str, Callable[[Any], Any]]


def _load_yaml(path: str) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load YAML mappings")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_mapping_config(path: str) -> MappingConfig:
    """Load a mapping configuration from *path*."""

    if path.endswith(('.yaml', '.yml')):
        data = _load_yaml(path)
    else:
        data = _load_json(path)

    fields: Mapping[str, Any] = data.get("fields", {})
    mapping: dict[str, str] = {}
    defaults: dict[str, Any] = {}
    transforms: dict[str, Callable[[Any], Any]] = {}

    for src, info in fields.items():
        if not isinstance(info, Mapping):
            continue
        target = info.get("target", src)
        mapping[src] = target
        if "default" in info:
            defaults[target] = info["default"]
        if "transform" in info:
            module_name, func_name = str(info["transform"]).rsplit(".", 1)
            module = import_module(module_name)
            func = getattr(module, func_name)
            if not callable(func):
                raise TypeError(f"Transform for {src} is not callable")
            transforms[src] = func  # type: ignore[assignment]

    return MappingConfig(mapping=mapping, defaults=defaults, transforms=transforms)


def validate_mapping_config(config: MappingConfig) -> None:
    """Validate a loaded :class:`MappingConfig`."""

    for key, func in config.transforms.items():
        if not callable(func):
            raise TypeError(f"Transform for {key} is not callable")
