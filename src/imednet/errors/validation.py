"""Validation errors."""

from .api import ApiError


class ValidationError(ApiError):
    """Raised when a request is malformed or validation fails (HTTP 400)."""
    pass

class BadRequestError(ValidationError):
    """Raised for HTTP 400 bad requests."""
    pass

class UnknownVariableTypeError(ValidationError):
    """Raised when an unrecognized variable type is encountered."""
    pass
