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
# Groups: (1) sensitive key, (2) key/value separator, (3) optional quote, (4) raw value.
_SENSITIVE_PATTERN = re.compile(
    rf"(?i)\b({'|'.join(_SENSITIVE_PATTERN_KEYS)})\b(\s*[:=]\s*)([\"']?)([^,;\r\n]*?)\3(?=,|;|$)"
)


def _replace_sensitive_match(match: re.Match[str]) -> str:
    """Replace sensitive part of a regex match with asterisks.

    Args:
        match: The regex match object.

    Returns:
        str: The redacted string.
    """
    return f"{match.group(1)}{match.group(2)}{match.group(3)}***{match.group(3)}"


def _redact_sensitive_value(value: Any) -> Any:
    """Recursively redact sensitive information from a value.

    Args:
        value: The value to redact (dict, list, str, etc.).

    Returns:
        Any: The redacted value.
    """
    if isinstance(value, dict):
        return {
            key: (
                "***"
                if str(key).lower() in _SENSITIVE_KEYS
                else _redact_sensitive_value(val)
            )
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [_redact_sensitive_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_sensitive_value(item) for item in value)
    if isinstance(value, str):
        return _SENSITIVE_PATTERN.sub(_replace_sensitive_match, value)
    return value


class ApiError(ImednetError):
    """Raised for generic API errors (non-2xx HTTP status codes).

    Attributes:
        status_code: HTTP status code returned by the API.
        response: Parsed JSON or raw text of the error response.
    """

    def __init__(
        self,
        response: Union[Dict[str, Any], str, Any],
        status_code: Optional[int] = None,
    ) -> None:
        """Initialize an API error.

        Args:
            response: The error response from the API.
            status_code: Optional HTTP status code.
        """
        sanitized_response = _redact_sensitive_value(response)

        message_arg = str(sanitized_response)
        parsed_message = None
        code = None
        status = None

        if isinstance(sanitized_response, dict):
            if "message" in sanitized_response:
                parsed_message = str(sanitized_response["message"])
            elif "error" in sanitized_response:
                parsed_message = str(sanitized_response["error"])

            if "code" in sanitized_response:
                try:
                    code = int(sanitized_response["code"])
                except (ValueError, TypeError):
                    pass

            if "status" in sanitized_response:
                status = str(sanitized_response["status"])

        super().__init__(message_arg, status_code=status_code, code=code, status=status)
        self.response = sanitized_response
        self.message = parsed_message if parsed_message is not None else message_arg

    def __str__(self) -> str:
        """Return a string representation of the error, including status and response.

        Returns:
            str: The formatted error message.
        """
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
