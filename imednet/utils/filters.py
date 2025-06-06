"""
Utility functions for building API filter strings.

This module provides functionality to construct filter query parameters
for iMednet API endpoints based on the reference documentation.
"""

from typing import Any, Dict, List, Tuple, Union

FilterValue = Union[Any, Tuple[str, Any], List[Any], Dict[str, Any]]


def build_filter_string(
    filters: Union[Dict[str, FilterValue], List[FilterValue], str],
    and_connector: str = ";",
    or_connector: str = ",",
) -> str:
    """Return a filter string for API requests.

    Args:
        filters: Mapping of filter keys to values or tuples or a pre-built string.
        and_connector: Connector for AND conditions.
        or_connector: Connector for OR conditions.

    Returns:
        String suitable for the ``filter`` query parameter.
    """

    if isinstance(filters, str):
        return filters

    def quote(val: Any) -> str:
        text = str(val)
        if any(c in text for c in (and_connector, or_connector, "(", ")", '"')):
            text = text.replace('"', '\\"')
            return f'"{text}"'
        return text

    def condition(key: str, value: FilterValue) -> str:
        if isinstance(value, dict):
            return parse(value)
        if isinstance(value, tuple) and len(value) == 2:
            op, val = value
            return f"{key}{op}{quote(val)}"
        if isinstance(value, list):
            sub = [f"{key}=={quote(v)}" for v in value]
            return or_connector.join(sub)
        return f"{key}=={quote(value)}"

    def parse(node: Union[Dict[str, FilterValue], List[FilterValue]], outer: bool = False) -> str:
        if isinstance(node, list):
            sub_parts = [parse(item) for item in node]
            joined = and_connector.join(sub_parts)
            return joined if outer else f"({joined})"

        parts: List[str] = []
        for k, v in node.items():
            if k in {"and", "or"}:
                if not isinstance(v, list):
                    raise ValueError(f"'{k}' value must be a list of filters")
                conn = and_connector if k == "and" else or_connector
                inner = [parse(item) for item in v]
                group = conn.join(inner)
                parts.append(group if outer else f"({group})")
            else:
                parts.append(condition(k, v))

        return and_connector.join(parts)

    result = parse(filters, outer=True)
    if result.startswith("(") and result.endswith(")"):
        result = result[1:-1]
    return result
