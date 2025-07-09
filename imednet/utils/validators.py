from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List, TypeVar

from imednet.utils.dates import parse_iso_datetime  # Centralized date parsing

T = TypeVar("T")


def _or_default(value: Any, default: Any) -> Any:
    """Return value if not None, else default."""
    return value if value is not None else default


def parse_datetime(v: str | datetime) -> datetime:
    """Parse an ISO datetime string or return a sentinel value.

    The SDK historically returns ``datetime(1969, 4, 20, 16, 20)`` when a
    timestamp field is empty. This helper mirrors that behaviour for backward
    compatibility.
    """
    if not v:
        return datetime(1969, 4, 20, 16, 20)
    if isinstance(v, str):
        return parse_iso_datetime(v)
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
        if val in ("true", "1", "yes", "y", "t"):
            return True
        if val in ("false", "0", "no", "n", "f"):
            return False
    if isinstance(v, (int, float)):
        return bool(v)
    return False


def parse_int_or_default(v: Any, default: int = 0, strict: bool = False) -> int:
    """
    Normalize integer values, defaulting if None or empty string.
    If strict=True, raise ValueError on parse failure.
    """
    if v is None or v == "":
        return default
    try:
        return int(v)
    except (ValueError, TypeError):
        if strict:
            raise
        return default


def parse_str_or_default(v: Any, default: str = "") -> str:
    """
    Normalize string values, defaulting if None.
    """
    return default if v is None else str(v)


def parse_list_or_default(v: Any, default_factory: Callable[[], List[T]] = list) -> List[T]:
    """
    Normalize list values, defaulting if None. Ensures result is a list.
    """
    if v is None:
        return default_factory()
    if isinstance(v, list):
        return v
    return [v]


def parse_dict_or_default(
    v: Any, default_factory: Callable[[], Dict[str, Any]] = dict
) -> Dict[str, Any]:
    """
    Normalize dictionary values, defaulting if None. Ensures result is a dict.
    """
    if v is None:
        return default_factory()
    if isinstance(v, dict):
        return v
    return default_factory()  # fallback if not a dict
