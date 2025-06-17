"""
Utility functions for building API filter strings.

This module provides functionality to construct filter query parameters
for iMednet API endpoints based on the reference documentation.
"""

import re
from typing import Any, Dict, List, Tuple, Union


def _snake_to_camel(text: str) -> str:
    """Convert a snake_case string to camelCase."""

    if "_" not in text:
        return text
    parts = text.split("_")
    first, rest = parts[0], parts[1:]
    return first + "".join(word.capitalize() for word in rest)


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

    def _format(val: Any) -> str:
        if isinstance(val, str):
            if re.search(r"[^A-Za-z0-9_.-]", val):
                escaped = val.replace('"', r"\"")
                return f'"{escaped}"'
            return val
        return str(val)

    parts: List[str] = []
    for key, value in filters.items():
        camel_key = _snake_to_camel(key)
        if isinstance(value, tuple) and len(value) == 2:
            op, val = value
            parts.append(f"{camel_key}{op}{_format(val)}")
        elif isinstance(value, list):
            subparts = [f"{camel_key}=={_format(v)}" for v in value]
            parts.append(or_connector.join(subparts))
        else:
            parts.append(f"{camel_key}=={_format(value)}")
    return and_connector.join(parts)
