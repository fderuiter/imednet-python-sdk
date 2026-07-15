"""Data serialization and flattening utilities."""

from typing import Any, Dict  # noqa: UP035


def flatten(data: Any, prefix: str = "") -> dict[str, Any]:
    """Recursively flatten a nested dict/list into dot-notation keys."""
    result: dict[str, Any] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            result.update(flatten(value, full_key))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            full_key = f"{prefix}[{index}]"
            result.update(flatten(item, full_key))
    else:
        result[prefix] = data
    return result


__all__ = ["flatten"]
