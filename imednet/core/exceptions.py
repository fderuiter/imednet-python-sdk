"""Placeholder for custom SDK exceptions."""

# Purpose:
# This module defines a hierarchy of custom exceptions specific to the iMednet SDK.
# This allows users to catch specific types of errors originating from API interactions.

# Implementation:
# 1. Define a base exception class, e.g., `ImednetError(Exception)`.
# 2. Define more specific exceptions inheriting from the base class:
#    - `ApiError(ImednetError)`: General error returned by the API (e.g., 4xx, 5xx).
#      - Could store status code, response body/message.
#    - `AuthenticationError(ApiError)`: Specifically for 401 Unauthorized.
#    - `NotFoundError(ApiError)`: Specifically for 404 Not Found.
#    - `RateLimitError(ApiError)`: Specifically for 429 Too Many Requests.
#    - `ServerError(ApiError)`: Specifically for 5xx errors.
#    - `RequestError(ImednetError)`: For errors occurring before/during the request
#       (e.g., network issues, timeouts).
#    - `ValidationError(ImednetError)`: For issues with input parameters provided by the user.

# Integration:
# - Raised by the `Client` when API calls fail.
# - Raised by `Endpoint` or `Workflow` methods for validation errors.
# - Users of the SDK can import and use these exceptions in their `try...except` blocks
#   for robust error handling.


class ImednetError(Exception):
    """Base class for all iMednet SDK errors."""

    pass


class RequestError(ImednetError):
    """Error related to making the HTTP request (network, timeout, etc.)."""

    pass


class ApiError(ImednetError):
    """Error reported by the Mednet API (4xx or 5xx status code)."""

    def __init__(
        self, message: str, status_code: int | None = None, response_body: dict | str | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        base = super().__str__()
        details = []
        if self.status_code:
            details.append(f"Status Code: {self.status_code}")
        if self.response_body:
            details.append(f"Response: {self.response_body}")
        return f"{base} ({', '.join(details)})" if details else base


class AuthenticationError(ApiError):
    """API authentication failed (401)."""

    pass


class NotFoundError(ApiError):
    """Resource not found (404)."""

    pass


class RateLimitError(ApiError):
    """Rate limit exceeded (429)."""

    pass


class ServerError(ApiError):
    """Internal server error on the API side (5xx)."""

    pass


class ValidationError(ImednetError):
    """Invalid input provided to an SDK method."""

    pass
