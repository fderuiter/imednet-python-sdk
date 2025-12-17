"""
Security utilities.
"""

from typing import Any


def sanitize_csv_formula(value: Any) -> Any:
    """
    Sanitize a value to prevent CSV/Excel Formula Injection.

    Prefixes strings starting with =, +, -, or @ with a single quote.
    """
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value
