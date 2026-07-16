"""Validation errors."""

from typing import Any, Dict, Optional, Union  # noqa: UP035

from .api import ApiError
from .client import ClientError


class ValidationError(ApiError):
    """Raised when a request is malformed or validation fails (HTTP 400)."""

    def __init__(self, response: dict[str, Any] | str | Any, status_code: int | None = 400) -> None:
        """Initialize validation error."""
        super().__init__(response, status_code=status_code)
        if not self.status:
            self.status = "validation_error"


class BadRequestError(ValidationError):
    """Raised for HTTP 400 bad requests."""

    pass


class UnknownVariableTypeError(ValidationError):
    """Raised when an unrecognized variable type is encountered."""

    pass


class ConfigurationError(ClientError):
    """Raised when required SDK/client configuration is missing."""

    pass


class PathTraversalValidationError(ClientError):
    """Raised when a partition key contains unsafe path content."""

    pass
