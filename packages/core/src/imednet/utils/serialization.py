"""TODO: Add docstring."""
from typing import Any, Dict


def flatten(data: Any, prefix: str = "") -> Dict[str, Any]:
    """Recursively flatten a nested dict/list into dot-notation keys."""
    result: Dict[str, Any] = {}
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
