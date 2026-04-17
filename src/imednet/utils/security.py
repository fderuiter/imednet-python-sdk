"""
Security utilities.
"""

from typing import Any
from imednet.errors import ClientError


def sanitize_csv_formula(value: Any) -> Any:
    """
    Sanitize a value to prevent CSV/Excel Formula Injection.

    Prefixes strings starting with =, +, -, or @ (even after whitespace) with a single quote.
    """
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
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
