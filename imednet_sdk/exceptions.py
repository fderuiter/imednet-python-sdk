"""Custom exceptions for the iMednet SDK.

This module defines a hierarchy of custom exception classes used throughout
the SDK to represent various errors that can occur during API interactions,
including network issues, authentication problems, API-specific errors,
and data validation failures.
"""

from typing import Any, Dict, Optional


class ImednetSdkException(Exception):
    """Base exception class for all iMednet SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_error_code: Optional[str] = None,
        request_path: Optional[str] = None,
        response_body: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,  # Consider using datetime object
    ):
        """Initializes the base SDK exception.

        Args:
            message: The main error message.
            status_code: The HTTP status code of the response, if applicable.
            api_error_code: The specific error code returned by the iMednet API,
                if applicable.
            request_path: The path of the API request that caused the error.
            response_body: The parsed JSON body of the error response, if available.
            timestamp: An ISO 8601 formatted timestamp string indicating when the
                error occurred.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.api_error_code = api_error_code
        self.request_path = request_path
        self.response_body = response_body
        self.timestamp = timestamp  # Store timestamp if available

    def __str__(self) -> str:
        """Returns a string representation of the exception including key details."""
        parts = [f"{self.__class__.__name__}: {self.message}"]
        if self.status_code:
            parts.append(f"Status Code: {self.status_code}")
        if self.api_error_code:
            parts.append(f"API Error Code: {self.api_error_code}")
        if self.request_path:
            parts.append(f"Request Path: {self.request_path}")
        # Avoid printing potentially large/sensitive response body by default
        # if self.response_body:
        #     parts.append(f"Response Body: {self.response_body}")
        return " | ".join(parts)


class ApiError(ImednetSdkException):
    """Raised for general API errors (e.g., 5xx server errors)."""

    pass


class AuthenticationError(ImednetSdkException):
    """Raised for authentication failures (e.g., 401 Unauthorized, invalid keys)."""

    pass


class AuthorizationError(ImednetSdkException):
    """Raised for authorization failures (e.g., 403 Forbidden, insufficient permissions)."""

    pass


class BadRequestError(ImednetSdkException):
    """Base class for 400-type client errors."""

    pass


class SdkValidationError(BadRequestError):
    """Raised when the iMednet API returns a validation error (code 1000).

    This error occurs when the API rejects the request due to validation failures,
    such as invalid field values, missing required fields, or data format issues.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = 400,
        api_error_code: Optional[str] = "1000",
        request_path: Optional[str] = None,
        response_body: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
    ):
        """Initialize a validation error with API-specific details.

        Args:
            message: The validation error message.
            status_code: HTTP status code (defaults to 400).
            api_error_code: API error code (defaults to "1000" for validation).
            request_path: The API endpoint path where validation failed.
            response_body: The full error response body from the API.
            timestamp: When the error occurred (ISO 8601 format).
        """
        super().__init__(
            message=message,
            status_code=status_code,
            api_error_code=api_error_code,
            request_path=request_path,
            response_body=response_body,
            timestamp=timestamp,
        )

    def __str__(self) -> str:
        """Returns a string representation including validation-specific details."""
        base_str = super().__str__()
        parts = [base_str]
        if self.attribute:
            parts.append(f"Attribute: {self.attribute}")
        if self.value is not None:  # Check for None explicitly
            parts.append(f"Value: {self.value}")
        return " | ".join(parts)


class NotFoundError(ImednetSdkException):
    """Raised when a requested resource is not found (e.g., 404 Not Found)."""

    pass


class RateLimitError(ImednetSdkException):
    """Raised when the API rate limit has been exceeded (e.g., 429 Too Many Requests)."""

    pass
