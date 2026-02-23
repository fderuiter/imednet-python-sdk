"""
Security utilities.
"""

from typing import Any


def sanitize_csv_formula(value: Any) -> Any:
    """
    Sanitize a value to prevent CSV/Excel Formula Injection.

    Prefixes strings starting with =, +, -, or @ (even after whitespace) with a single quote.
    """
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


def validate_header_value(value: str) -> str:
    """
    Validate that a header value does not contain newlines to prevent header injection.

    Args:
        value: The header value to validate.

    Returns:
        The validated value.

    Raises:
        ValueError: If the value contains newlines.
    """
    if "\n" in value or "\r" in value:
        raise ValueError("Header value must not contain newlines")
    return value
