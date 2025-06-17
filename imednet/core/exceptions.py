"""
Custom exceptions for the iMednet SDK.

Defines a hierarchy of exceptions corresponding to HTTP and validation errors.
"""

from typing import Any, Optional


class ImednetError(Exception):
    """
    Base exception for all iMednet SDK errors.
    """

    pass


class RequestError(ImednetError):
    """
    Raised when a network request fails after retries.
    """

    pass


class ApiError(ImednetError):
    """
    Raised for generic API errors (non-2xx HTTP status codes).

    Attributes:
        status_code: HTTP status code returned by the API.
        response: Parsed JSON or raw text of the error response.
    """

    def __init__(self, response: Any, status_code: Optional[int] = None) -> None:
        super().__init__(str(response))
        self.status_code = status_code
        self.response = response

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
    """
    Raised when authentication to the API fails (HTTP 401).
    """

    pass


class AuthorizationError(ApiError):
    """
    Raised when access to the API is forbidden (HTTP 403).
    """

    pass


class NotFoundError(ApiError):
    """
    Raised when a requested resource is not found (HTTP 404).
    """

    pass


class RateLimitError(ApiError):
    """
    Raised when the API rate limit is exceeded (HTTP 429).
    """

    pass


class ServerError(ApiError):
    """
    Raised when the API returns a server error (HTTP 5xx).
    """

    pass


class ValidationError(ApiError):
    """
    Raised when a request is malformed or validation fails (HTTP 400).
    """

    pass


class BadRequestError(ValidationError):
    """Raised for HTTP 400 bad requests."""

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


class UnknownVariableTypeError(ValidationError):
    """Raised when an unrecognized variable type is encountered."""

    pass
