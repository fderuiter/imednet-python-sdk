"""
Utility functions for building API filter strings.

This module provides functionality to construct filter query parameters
for iMednet API endpoints based on the reference documentation.
"""

from typing import Any, Dict, List, Tuple, Union


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
    parts: List[str] = []
    for key, value in filters.items():
        if isinstance(value, tuple) and len(value) == 2:
            op, val = value
            parts.append(f"{key}{op}{val}")
        elif isinstance(value, list):
            subparts = [f"{key}=={v}" for v in value]
            parts.append(or_connector.join(subparts))
        else:
            parts.append(f"{key}=={value}")
    return and_connector.join(parts)
