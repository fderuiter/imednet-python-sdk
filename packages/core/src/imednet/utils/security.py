"""Security utilities."""

import re
from typing import Any

from imednet.errors import ClientError, PathTraversalValidationError

_WINDOWS_ABSOLUTE_PATH_RE = re.compile(r"^[A-Za-z]:[/\\]")


class SensitivityRegistry:
    """Registry for managing sensitive fields (PHI) that should be masked in logs."""

    def __init__(self) -> None:
        """Initialize the registry with default sensitive and exempt keys."""
        # Default clinical PHI fields
        self._sensitive_keys = {
            "patient_name",
            "patient_initials",
            "dob",
            "date_of_birth",
            "ssn",
            "phone",
            "email",
            "address",
            "birth_date",
        }
        # Keys explicitly exempted from masking
        self._exempt_keys = {"subject_key", "study_key", "record_id"}

    def add_sensitive_key(self, key: str) -> None:
        """Add a key to the sensitive list if it is not exempted."""
        if key not in self._exempt_keys:
            self._sensitive_keys.add(key)

    def remove_sensitive_key(self, key: str) -> None:
        """Remove a key from the sensitive list."""
        self._sensitive_keys.discard(key)

    def add_exempt_key(self, key: str) -> None:
        """Add a key to the exemption list."""
        self._exempt_keys.add(key)

    def remove_exempt_key(self, key: str) -> None:
        """Remove a key from the exemption list."""
        self._exempt_keys.discard(key)

    def is_sensitive(self, key: str) -> bool:
        """Check if a key is considered sensitive and not exempted."""
        if key in self._exempt_keys:
            return False
        return key in self._sensitive_keys


global_sensitivity_registry = SensitivityRegistry()


def mask_clinical_phi(value: Any) -> Any:
    """Recursively mask sensitive keys in unstructured data."""
    if isinstance(value, dict):
        return {
            k: (
                "***MASKED***"
                if global_sensitivity_registry.is_sensitive(k)
                else mask_clinical_phi(v)
            )
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [mask_clinical_phi(v) for v in value]
    if isinstance(value, tuple):
        return tuple(mask_clinical_phi(v) for v in value)
    return value


def sanitize_csv_formula(value: Any) -> Any:
    """Sanitize a value to prevent CSV/Excel Formula Injection.

    Prefixes strings starting with =, +, -, or @ (even after whitespace) with a single quote.
    Lists and tuples are recursively sanitized.
    """
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
    if isinstance(value, list):
        return [sanitize_csv_formula(v) for v in value]
    if isinstance(value, tuple):
        return tuple(sanitize_csv_formula(v) for v in value)
    return value


def validate_header_value(value: str) -> None:
    """Validate that a header value does not contain newline characters.

    Args:
        value: The header value to validate.

    Raises:
        ClientError: If the value contains newline characters.
    """
    if "\n" in value or "\r" in value:
        raise ClientError(f"Header value must not contain newlines: {value!r}")


def validate_partition_key(key: str) -> None:
    """Reject partition keys that could escape or reshape the target directory."""
    if "\x00" in key:
        raise PathTraversalValidationError(f"Partition key must not contain null bytes: {key!r}")
    if key.startswith(("/", "\\")) or _WINDOWS_ABSOLUTE_PATH_RE.match(key):
        raise PathTraversalValidationError(
            f"Partition key must not use absolute path modifiers: {key!r}"
        )
    if "../" in key or "..\\" in key or key == "..":
        raise PathTraversalValidationError(
            f"Partition key must not contain parent-directory traversal: {key!r}"
        )
    if "/" in key or "\\" in key:
        raise PathTraversalValidationError(
            f"Partition key must not contain path separators: {key!r}"
        )
