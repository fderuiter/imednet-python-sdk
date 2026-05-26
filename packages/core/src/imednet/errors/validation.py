"""Validation errors."""

from .api import ApiError
from .client import ClientError


class ValidationError(ApiError):
    """Raised when a request is malformed or validation fails (HTTP 400)."""

    pass


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
