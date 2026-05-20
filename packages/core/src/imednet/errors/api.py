"""API-level errors."""

import re
from typing import Any, Dict, Optional, Union

from .base import ImednetError

_SENSITIVE_KEYS = {
    "api_key",
    "security_key",
    "token",
    "authorization",
    "x-api-key",
    "x-imn-security-key",
}
_SENSITIVE_PATTERN_KEYS = (
    "x-imn-security-key",
    "x-api-key",
    "api[_-]?key",
    "security[_-]?key",
    "authorization",
    "token",
)
_SENSITIVE_PATTERN = re.compile(
    rf"(?i)\b({'|'.join(_SENSITIVE_PATTERN_KEYS)})\b(\s*[:=]\s*)([\"']?)([^,;\"'\s]+)\3"
)


def _redact_sensitive_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: ("***" if str(key).lower() in _SENSITIVE_KEYS else _redact_sensitive_value(val))
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [_redact_sensitive_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_sensitive_value(item) for item in value)
    if isinstance(value, str):
        return _SENSITIVE_PATTERN.sub(
            lambda match: f"{match.group(1)}{match.group(2)}{match.group(3)}***{match.group(3)}",
            value,
        )
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
