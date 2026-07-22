"""API-level errors."""

from typing import Any

from imednet.utils.secrets import redact_sensitive_payload as _redact_sensitive_value

from .base import ImednetError


class ApiError(ImednetError):
    """Raised for generic API errors (non-2xx HTTP status codes).

    Attributes:
        status_code: HTTP status code returned by the API.
        response: Parsed JSON or raw text of the error response.
    """

    def __init__(
        self, response: dict[str, Any] | str | Any, status_code: int | None = None
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
                try:  # noqa: SIM105
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


class AuthorizationError(ApiError):
    """Raised when access to the API is forbidden (HTTP 403)."""


class NotFoundError(ApiError):
    """Raised when a requested resource is not found (HTTP 404)."""


class RateLimitError(ApiError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""


class ServerError(ApiError):
    """Raised when the API returns a server error (HTTP 5xx)."""


class UnauthorizedError(AuthenticationError):
    """Raised for HTTP 401 unauthorized errors."""


class ForbiddenError(AuthorizationError):
    """Raised for HTTP 403 forbidden errors."""


class ConflictError(ApiError):
    """Raised for HTTP 409 conflict errors."""
