from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List, TypeVar

T = TypeVar("T")


def parse_datetime(v: str | datetime) -> datetime:
    """
    Normalize datetime values.
    If missing or falsy, default to Jan 1st, 1900;
        if string, normalize any space to 'T' and parse ISO format.
    """
    if not v:
        return datetime(1900, 1, 1)
    if isinstance(v, str):
        # Normalize space to 'T' for ISO format
        return datetime.fromisoformat(v.replace(" ", "T"))
    return v


def parse_bool(v: Any) -> bool:
    """
    Normalize boolean values from various representations.
    Accepts bool, str, int, float and returns a bool.
    """
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        val = v.strip().lower()
        if val in ("true", "1", "yes", "y", "t"):  # truthy strings
            return True
        if val in ("false", "0", "no", "n", "f"):  # falsy strings
            return False
    if isinstance(v, (int, float)):
        return bool(v)
    return False


def parse_int_or_default(v: Any, default: int = 0) -> int:
    """
    Normalize integer values, defaulting if None or empty string.
    """
    if v is None or v == "":
        return default
    try:
        return int(v)
    except (ValueError, TypeError):
        return default  # Or raise a validation error if strict parsing is needed


def parse_str_or_default(v: Any, default: str = "") -> str:
    """
    Normalize string values, defaulting if None.
    """
    if v is None:
        return default
    return str(v)


def parse_list_or_default(v: Any, default_factory: Callable[[], List[T]] = list) -> List[T]:
    """
    Normalize list values, defaulting if None.
    """
    if v is None:
        return default_factory()
    # Could add type check here if needed: isinstance(v, list)
    return v


def parse_dict_or_default(
    v: Any, default_factory: Callable[[], Dict[str, Any]] = dict
) -> Dict[str, Any]:
    """
    Normalize dictionary values, defaulting if None.
    """
    if v is None:
        return default_factory()
    # Could add type check here if needed: isinstance(v, dict)
    return v
