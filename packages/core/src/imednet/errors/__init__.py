"""Exception hierarchy."""

from .api import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
)
from .base import ImednetError
from .client import ClientError, PaginationError
from .network import RequestError
from .plugin import PluginLoadError
from .registry import get_error_class
from .validation import (
    BadRequestError,
    ConfigurationError,
    UnknownVariableTypeError,
    ValidationError,
)

__all__ = [
    "get_error_class",
    "ImednetError",
    "PluginLoadError",
    "RequestError",
    "ClientError",
    "PaginationError",
    "ApiError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    "ConfigurationError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "UnknownVariableTypeError",
]
