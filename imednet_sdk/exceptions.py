"""Custom exceptions for the iMednet SDK."""

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
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.api_error_code = api_error_code
        self.request_path = request_path
        self.response_body = response_body
        self.timestamp = timestamp  # Store timestamp if available

    def __str__(self) -> str:
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
    """Raised for general bad requests (e.g., 400 Bad Request)."""

    pass


class ValidationError(BadRequestError):
    """Raised specifically for validation errors (API error code 1000)."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_error_code: Optional[str] = None,
        request_path: Optional[str] = None,
        response_body: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
        attribute: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            api_error_code=api_error_code,
            request_path=request_path,
            response_body=response_body,
            timestamp=timestamp,
        )
        self.attribute = attribute
        self.value = value

    def __str__(self) -> str:
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
    """Raised when API rate limits are exceeded (e.g., 429 Too Many Requests)."""

    pass
