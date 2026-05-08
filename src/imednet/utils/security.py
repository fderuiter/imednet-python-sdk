"""
Security utilities.
"""

from typing import Any

from imednet.errors import ClientError


def sanitize_csv_formula(value: Any) -> Any:
    """
    Sanitize a value to prevent CSV/Excel Formula Injection.

    Prefixes strings starting with =, +, -, or @ (even after whitespace) with a single quote.
    Lists and tuples are recursively sanitized.
    """
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
    elif isinstance(value, list):
        return [sanitize_csv_formula(v) for v in value]
    elif isinstance(value, tuple):
        return tuple(sanitize_csv_formula(v) for v in value)
    return value


def validate_header_value(value: str) -> None:
    """
    Validate that a header value does not contain newline characters.

    Args:
        value: The header value to validate.

    Raises:
        ClientError: If the value contains newline characters.
    """
    if "\n" in value or "\r" in value:
        raise ClientError(f"Header value must not contain newlines: {value!r}")
