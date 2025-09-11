from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List, TypeVar

from imednet.utils.dates import parse_iso_datetime  # Centralized date parsing

T = TypeVar("T")


def _or_default(value: Any, default: Any) -> Any:
    """Return the value if it is not None, otherwise return the default.

    Args:
        value: The value to check.
        default: The default value to return if `value` is `None`.

    Returns:
        The value or the default.
    """
    return value if value is not None else default


def parse_datetime(v: str | datetime) -> datetime:
    """Parse a datetime from a string or return a sentinel for empty values.

    This function handles ISO datetime strings and maintains backward
    compatibility by returning a specific sentinel datetime for empty inputs.

    Args:
        v: The value to parse, which can be a string or a datetime object.

    Returns:
        A datetime object.
    """
    if not v:
        return datetime(1969, 4, 20, 16, 20)
    if isinstance(v, str):
        return parse_iso_datetime(v)
    return v


def parse_bool(v: Any) -> bool:
    """Normalize a value to a boolean.

    This function handles boolean, string, integer, and float inputs and
    converts them to a boolean value.

    Args:
        v: The value to normalize.

    Returns:
        The normalized boolean value.
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
    if isinstance(v, str):
        raise ValueError(f"Could not parse boolean from string: {v}")
    return False


def parse_int_or_default(v: Any, default: int = 0, strict: bool = False) -> int:
    """Normalize a value to an integer, with a fallback to a default.

    Args:
        v: The value to normalize.
        default: The default value to return if `v` is `None` or an empty string.
        strict: If `True`, raise a `ValueError` on parsing failure.

    Returns:
        The normalized integer value.
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
    """Normalize a value to a string, with a fallback to a default.

    Args:
        v: The value to normalize.
        default: The default value to return if `v` is `None`.

    Returns:
        The normalized string value.
    """
    return default if v is None else str(v)


def parse_list_or_default(v: Any, default_factory: Callable[[], List[T]] = list) -> List[T]:
    """Normalize a value to a list, with a fallback to a default.

    If the value is not a list, it will be wrapped in a list.

    Args:
        v: The value to normalize.
        default_factory: A function that returns the default list.

    Returns:
        The normalized list.
    """
    if v is None:
        return default_factory()
    if isinstance(v, list):
        return v
    return [v]


def parse_dict_or_default(
    v: Any, default_factory: Callable[[], Dict[str, Any]] = dict
) -> Dict[str, Any]:
    """Normalize a value to a dictionary, with a fallback to a default.

    Args:
        v: The value to normalize.
        default_factory: A function that returns the default dictionary.

    Returns:
        The normalized dictionary.

    Raises:
        TypeError: If the value is not a dictionary or None.
    """
    if v is None:
        return default_factory()
    if isinstance(v, dict):
        return v
    raise TypeError(f"Expected a dictionary, but got {type(v).__name__}")
