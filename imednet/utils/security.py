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


def validate_header_value(name: str, value: str) -> None:
    """
    Validate a header value to prevent header injection.

    Args:
        name: The name of the header (for error messages).
        value: The value to validate.

    Raises:
        ValueError: If the value contains newlines.
    """
    if "\n" in value or "\r" in value:
        raise ValueError(f"{name} must not contain newlines")
