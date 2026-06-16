"""
Universal Security & Logging Framework
"""

import logging
import re
import urllib.parse
from typing import Any

_WINDOWS_ABSOLUTE_PATH_RE = re.compile(r"^[A-Za-z]:[/\\]")

class SensitivityRegistry:
    def __init__(self) -> None:
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
        self._sensitive_patterns = {
            "password",
            "token",
            "secret",
            "credential",
            "api_key",
            "apikey",
            "auth_key",
            "access_key",
            "security_key",
            "private_key",
            "client_secret",
            "authorization",
            "api[_-]?key",
            "security[_-]?key",
        }
        self._exempt_keys = {"subject_key", "study_key", "record_id"}

    def add_sensitive_key(self, key: str) -> None:
        if key not in self._exempt_keys:
            self._sensitive_keys.add(key)

    def remove_sensitive_key(self, key: str) -> None:
        self._sensitive_keys.discard(key)
        
    def add_sensitive_pattern(self, pattern: str) -> None:
        self._sensitive_patterns.add(pattern)

    def add_exempt_key(self, key: str) -> None:
        self._exempt_keys.add(key)

    def remove_exempt_key(self, key: str) -> None:
        self._exempt_keys.discard(key)

    def is_sensitive(self, key: str) -> bool:
        if key in self._exempt_keys:
            return False
        if key in self._sensitive_keys:
            return True
        key_lower = str(key).lower()
        if any(re.search(pattern, key_lower) for pattern in self._sensitive_patterns):
            return True
        return False

global_sensitivity_registry = SensitivityRegistry()

_REDACTION_MARKER = "***MASKED***"

def mask_clinical_phi(value: Any) -> Any:
    """Recursively mask sensitive keys in unstructured data."""
    if isinstance(value, dict):
        redacted = {}
        for k, v in value.items():
            if global_sensitivity_registry.is_sensitive(str(k)):
                redacted[k] = _REDACTION_MARKER
            else:
                redacted[k] = mask_clinical_phi(v)
        return redacted
    elif isinstance(value, list):
        return [mask_clinical_phi(v) for v in value]
    elif isinstance(value, tuple):
        return tuple(mask_clinical_phi(v) for v in value)
    return value

def sanitize_csv_formula(value: Any) -> Any:
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
    elif isinstance(value, list):
        return [sanitize_csv_formula(v) for v in value]
    elif isinstance(value, tuple):
        return tuple(sanitize_csv_formula(v) for v in value)
    return value

def validate_header_value(value: str) -> None:
    from imednet.errors import ClientError
    if "\n" in value or "\r" in value:
        raise ClientError(f"Header value must not contain newlines: {value!r}")

def validate_partition_key(key: str) -> None:
    from imednet.errors import PathTraversalValidationError
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

def redact_urls_in_string(text: str) -> str:
    """Masks credentials within URIs in a string."""
    def _mask_uri(match: re.Match) -> str:
        uri = match.group(0)
        try:
            parsed = urllib.parse.urlsplit(uri)
            if parsed.password or parsed.username:
                # Rebuild URI with masked credentials
                netloc = ""
                if parsed.username:
                    netloc += "***MASKED***"
                if parsed.password:
                    netloc += ":***MASKED***"
                netloc += f"@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                masked_uri = urllib.parse.urlunsplit((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.query,
                    parsed.fragment
                ))
                return masked_uri
        except ValueError:
            pass
        return uri

    # Find URIs containing credentials
    return re.sub(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^ ]+", _mask_uri, text)

class RedactionLogFilter(logging.Filter):
    """
    Filters all log messages and redacts connection strings, URIs with credentials,
    and unstructured data matching the SensitivityRegistry.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_urls_in_string(record.msg)
            
        if isinstance(record.args, dict):
            record.args = mask_clinical_phi(record.args)
        elif isinstance(record.args, tuple):
            record.args = mask_clinical_phi(record.args)
            
        return True
