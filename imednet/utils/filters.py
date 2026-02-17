"""
Utility functions for building API filter strings.

This module provides functionality to construct filter query parameters
for iMednet API endpoints based on the reference documentation.
"""

import functools
import re
from typing import Any, Dict, List, Tuple, Union

# Pre-compiled regex for performance to avoid re-compilation in loops
_UNSAFE_CHARS_REGEX = re.compile(r"[^A-Za-z0-9_.-]")


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
        if not val:
            return '""'
        if _UNSAFE_CHARS_REGEX.search(val):
            # Escape backslashes first to prevent escape injection
            escaped = val.replace("\\", "\\\\").replace('"', r"\"")
            return f'"{escaped}"'
        return val
    return str(val)


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

    parts: List[str] = []
    for key, value in filters.items():
        camel_key = _snake_to_camel(key)
        if isinstance(value, tuple) and len(value) == 2:
            op, val = value
            parts.append(f"{camel_key}{op}{_format_filter_value(val)}")
        elif isinstance(value, list):
            subparts = [f"{camel_key}=={_format_filter_value(v)}" for v in value]
            parts.append(or_connector.join(subparts))
        else:
            parts.append(f"{camel_key}=={_format_filter_value(value)}")
    return and_connector.join(parts)
