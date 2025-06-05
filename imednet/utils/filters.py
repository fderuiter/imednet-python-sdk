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
    """Return a filter string for API requests.

    Args:
        filters: Mapping of filter keys to values or tuples.
        and_connector: Connector for AND conditions.
        or_connector: Connector for OR conditions.

    Returns:
        String suitable for the ``filter`` query parameter.
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
