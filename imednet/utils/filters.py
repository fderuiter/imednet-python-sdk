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
    """
    Build a filter string for API requests from a mapping of filters.

    Strings are constructed according to the iMednet API filtering rules:
    - Use '<', '<=', '>', '>=', '==', '!=', '=~' operators.
    - Multiple conditions are joined by ';' (AND) or ',' (OR).
    - String values containing spaces or special characters are wrapped in
      double quotes.

    Args:
        filters: A dict where:
            - value is a raw value -> equality is assumed (==).
            - value is a tuple (op, val) -> use provided operator.
            - value is a list -> multiple equality filters OR-ed.
        and_connector: String connector for AND conditions (default ';').
        or_connector: String connector for OR conditions (default ',').

    Returns:
        A filter string suitable for use as a `filter` query parameter.

    Examples:
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
