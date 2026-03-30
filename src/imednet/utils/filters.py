"""
Utility functions for building API filter strings.

This module provides functionality to construct filter query parameters
for iMednet API endpoints based on the reference documentation.
"""

import functools
import re
from typing import Any, Dict, List, Tuple, TypeVar, Union

# Pre-compiled regex for performance to avoid re-compilation in loops
_UNSAFE_CHARS_REGEX = re.compile(r"[^A-Za-z0-9_.-]")

T = TypeVar("T")


@functools.lru_cache(maxsize=128)
def _snake_to_camel(text: str) -> str:
    """Convert a snake_case string to camelCase."""

    if "_" not in text:
        return text
    parts = text.split("_")
    first, rest = parts[0], parts[1:]
    return first + "".join(word.capitalize() for word in rest)


def _format_filter_value(val: Any) -> str:
    """Format a single filter value, escaping if necessary."""
    if isinstance(val, str):
        if _UNSAFE_CHARS_REGEX.search(val):
            # Escape backslashes first to prevent escape injection
            escaped = val.replace("\\", "\\\\").replace('"', r"\"")
            return f'"{escaped}"'
        return val
    return str(val)


def _build_filter_part(key: str, value: Union[Any, Tuple[str, Any], List[Any]], or_connector: str = ",") -> str:
    """
    Build a single filter string part from a key and value.
    """
    camel_key = _snake_to_camel(key)
    if isinstance(value, tuple) and len(value) == 2:
        op, val = value
        return f"{camel_key}{op}{_format_filter_value(val)}"
    elif isinstance(value, list):
        subparts = [f"{camel_key}=={_format_filter_value(v)}" for v in value]
        return or_connector.join(subparts)
    else:
        return f"{camel_key}=={_format_filter_value(value)}"


def build_filter_string(
    filters: Dict[str, Union[Any, Tuple[str, Any], List[Any]]],
    and_connector: str = ";",
    or_connector: str = ",",
) -> str:
    """Return a filter string constructed according to iMednet rules.

    Each key in ``filters`` is converted to camelCase. Raw values imply
    equality, tuples allow explicit operators, and lists generate multiple
    equality filters joined by ``or_connector``. Conditions are then joined by
    ``and_connector``.

    Examples
    --------
    >>> build_filter_string({'age': ('>', 30), 'status': 'active'})
    'age>30;status==active'
    >>> build_filter_string({'type': ['A', 'B']})
    'type==A,type==B'
    """

    parts = [_build_filter_part(key, value, or_connector) for key, value in filters.items()]
    return and_connector.join(parts)


def filter_by_attribute(items: List[T], attr_name: str, target_value: Any) -> List[T]:
    """
    Filter a list of objects by a specific attribute value using strict string comparison.

    This function handles the common case where API IDs might be returned as integers
    or strings, ensuring consistent comparison by converting both to strings.

    Args:
        items: List of objects to filter.
        attr_name: The name of the attribute to check on each object.
        target_value: The value to filter for.

    Returns:
        A new list containing only the items where the attribute matches the target value.
    """
    target_str = str(target_value)
    filtered_items = []
    for item in items:
        # Use getattr to safely access the attribute
        attr_val = getattr(item, attr_name, None)
        if attr_val is not None and str(attr_val) == target_str:
            filtered_items.append(item)
    return filtered_items
