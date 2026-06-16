"""API-level errors."""

import re
from typing import Any, Dict, Optional, Union

from imednet.security import global_sensitivity_registry, redact_urls_in_string

from .base import ImednetError

# We keep this regex logic here to redact key=value pairs in error strings
# but base the patterns on the global registry patterns if needed, or we just
# use the same regex but without the redundant list if possible.
# Actually, the task says "A single Sensitivity Registry replaces the multiple divergent lists"
# Let's import the patterns from the registry, but the registry patterns are substrings.
# We can just build the regex using the registry patterns.

_SENSITIVE_PATTERN = re.compile(
    rf"(?i)\b({'|'.join(global_sensitivity_registry._sensitive_patterns)})\b(\s*[:=]\s*)([\"']?)([^,;\r\n]*?)\3(?=,|;|$)"
)

def _replace_sensitive_match(match: re.Match[str]) -> str:
    return f"{match.group(1)}{match.group(2)}{match.group(3)}***MASKED***{match.group(3)}"


def _redact_sensitive_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: ("***MASKED***" if global_sensitivity_registry.is_sensitive(str(key)) else _redact_sensitive_value(val))
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [_redact_sensitive_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_sensitive_value(item) for item in value)
    if isinstance(value, str):
        # We also redact URLs containing credentials as part of string redaction
        val = redact_urls_in_string(value)
        return _SENSITIVE_PATTERN.sub(_replace_sensitive_match, val)
    return value


class ApiError(ImednetError):
    """
    Raised for generic API errors (non-2xx HTTP status codes).

    Attributes:
        status_code: HTTP status code returned by the API.
        response: Parsed JSON or raw text of the error response.
    """

    def __init__(
        self, response: Union[Dict[str, Any], str, Any], status_code: Optional[int] = None
    ) -> None:
        sanitized_response = _redact_sensitive_value(response)
        super().__init__(str(sanitized_response))
        self.status_code = status_code
        self.response = sanitized_response

    def __str__(self) -> str:
        base = super().__str__()
        details = []
        if self.status_code is not None:
            details.append(f"Status Code: {self.status_code}")
        if self.response:
            details.append(f"Response: {self.response}")
        if details:
            return f"{base} ({', '.join(details)})"
        return base


class AuthenticationError(ApiError):
    """Raised when authentication to the API fails (HTTP 401)."""

    pass


class AuthorizationError(ApiError):
    """Raised when access to the API is forbidden (HTTP 403)."""

    pass


class NotFoundError(ApiError):
    """Raised when a requested resource is not found (HTTP 404)."""

    pass


class RateLimitError(ApiError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""

    pass


class ServerError(ApiError):
    """Raised when the API returns a server error (HTTP 5xx)."""

    pass


class UnauthorizedError(AuthenticationError):
    """Raised for HTTP 401 unauthorized errors."""

    pass


class ForbiddenError(AuthorizationError):
    """Raised for HTTP 403 forbidden errors."""

    pass


class ConflictError(ApiError):
    """Raised for HTTP 409 conflict errors."""

    pass
