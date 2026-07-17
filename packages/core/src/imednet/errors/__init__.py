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
from .export import ExportBatchError, ExportConfigurationError, ExportError
from .network import RequestError
from .orchestration import FilterConflictError, OrchestratorError
from .plugin import PluginLoadError
from .registry import get_error_class
from .validation import (
    BadRequestError,
    ConfigurationError,
    PathTraversalValidationError,
    UnknownVariableTypeError,
    ValidationError,
)

__all__ = [
    "ApiError",
    "AuthenticationError",
    "AuthorizationError",
    "BadRequestError",
    "ClientError",
    "ConfigurationError",
    "ConflictError",
    "ExportBatchError",
    "ExportConfigurationError",
    "ExportError",
    "FilterConflictError",
    "ForbiddenError",
    "ImednetError",
    "NotFoundError",
    "OrchestratorError",
    "PaginationError",
    "PathTraversalValidationError",
    "PluginLoadError",
    "RateLimitError",
    "RequestError",
    "ServerError",
    "UnauthorizedError",
    "UnknownVariableTypeError",
    "ValidationError",
    "get_error_class",
]

for _name in __all__:
    _cls = globals().get(_name)
    if isinstance(_cls, type):
        _cls.__module__ = "imednet.errors"
